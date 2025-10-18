import time
from typing import Any

from EDAP_data import FlagsBeingInterdicted


def _get_station_type(ship_data: Any) -> str | None:
    """Return the current station type from ship data."""
    if ship_data is None:
        return None

    if hasattr(ship_data, "cur_station_type"):
        station_type = getattr(ship_data, "cur_station_type")
    elif isinstance(ship_data, dict):
        station_type = ship_data.get("cur_station_type")
    else:
        station_type = None

    if isinstance(station_type, str):
        station_type = station_type.strip()

    return station_type or None


def _is_interdicted(status: Any) -> bool:
    """Best-effort check to see if we are interdicted."""
    try:
        return bool(status.is_interdicted())
    except AttributeError:
        pass

    try:
        return bool(status.get_flag(FlagsBeingInterdicted))
    except AttributeError:
        pass

    current_data = getattr(status, "current_data", {}) or {}
    if isinstance(current_data, dict):
        if current_data.get("Interdicted") or current_data.get("Being Interdicted"):
            return True
    return False


def _get_target_coordinates(ship_data: Any) -> tuple[float | None, float | None, float | None]:
    """Extract target latitude, longitude and altitude from ship data."""

    lat = lon = alt = None

    if hasattr(ship_data, "target_latitude") or hasattr(ship_data, "target_longitude"):
        lat = getattr(ship_data, "target_latitude", None)
        lon = getattr(ship_data, "target_longitude", None)
        alt = getattr(ship_data, "target_altitude", None)
    elif isinstance(ship_data, dict):
        lat = ship_data.get("target_latitude")
        lon = ship_data.get("target_longitude")
        alt = ship_data.get("target_altitude")

    return lat, lon, alt


def DropOut_context(ship_data, status, keys, nav_panel, logger):
    """
    Визначає контекст після виходу із Supercruise.
    Повертає один із рядків:
    'surface_approach', 'station_docking', 'reengage_supercruise', 'recover_from_interdiction'.
    """
    context: str | None = None

    if _is_interdicted(status):
        keys.send("UseBoostJuice")
        time.sleep(2)
        keys.send("Supercruise")
        logger.warning("Interdiction detected — recovering and reengaging Supercruise")
        context = "recover_from_interdiction"
    else:
        station_type = _get_station_type(ship_data)
        if not station_type:
            logger.warning("Невідомий тип станції — повертаю reengage_supercruise")
            context = "reengage_supercruise"
        else:
            normalized_type = station_type.lower()
            if any(keyword in normalized_type for keyword in ("planetary", "surface", "altitude", "glide")):
                try:
                    from sc_assist import sc_target_align
                except ImportError as exc:
                    logger.error(f'Не вдалося імпортувати sc_target_align: {exc}')
                    context = "reengage_supercruise"
                    logger.info(f"DropOut завершено — повертаю контекст: {context}")
                    return context

                keys.send("SetSpeed100")
                loop_context: str | None = None
                for _ in range(120):
                    status.get_cleaned_data()
                    altitude = status.current_data.get("Altitude", 99999) if status.current_data else 99999
                    target_lat, target_lon, target_alt = _get_target_coordinates(ship_data)
                    distance = status.get_distance_to_target(target_lat, target_lon, target_alt)

                    if distance is not None:
                        logger.debug(f"DistanceToTarget: {distance:.0f} м")
                    else:
                        logger.debug("DistanceToTarget: невідомо")

                    sc_target_align()

                    if altitude < 20000:
                        keys.send("SetSpeed50")
                    if altitude < 10000:
                        keys.send("SetSpeed25")
                    if altitude < 7000 and distance is not None and distance < 10000:
                        logger.info(f"Approach complete — {distance/1000:.1f} км до станції, переходжу до докування")
                        loop_context = "station_docking"
                        break
                    if altitude < 5000:
                        logger.warning("Altitude < 5 km — уникаю зіткнення")
                        loop_context = "surface_approach"
                        break

                    pitch = status.current_data.get("Pitch", 0) if status.current_data else 0
                    if distance is not None:
                        logger.info(f"Altitude {altitude:.0f}м, Distance {distance/1000:.1f} км — продовжую Glide")
                    else:
                        logger.info(f"Altitude {altitude:.0f}м, Distance невідомо — продовжую Glide")

                    if abs(pitch) > 45:
                        keys.send("SetSpeedZero")
                        logger.warning("Кут занадто великий — стабілізую")

                    time.sleep(0.5)

                if loop_context is None:
                    logger.warning("Timeout 60s — Glide або Approach не виявлено")
                    loop_context = "surface_approach"

                context = loop_context
            elif "station" in normalized_type or "coriolis" in normalized_type:
                logger.info("Виявлено орбітальну станцію — перехід у режим докування")
                context = "station_docking"
            else:
                keys.send("Supercruise")
                logger.info("Невідомий тип об’єкта — повторний вихід у Supercruise")
                context = "reengage_supercruise"

    if context is None:
        context = "reengage_supercruise"

    logger.info(f"DropOut завершено — повертаю контекст: {context}")
    return context
