from enrichment_engine.staticmap import TILE_SIZE, _lonlat_to_pixel


def test_pixel_position_increases_with_longitude():
    x_west, _ = _lonlat_to_pixel(9.0, 56.0, zoom=16)
    x_east, _ = _lonlat_to_pixel(10.0, 56.0, zoom=16)
    assert x_east > x_west


def test_pixel_position_decreases_going_north():
    # Web Mercator: y increases southward, so higher latitude -> smaller y.
    _, y_north = _lonlat_to_pixel(10.0, 60.0, zoom=16)
    _, y_south = _lonlat_to_pixel(10.0, 50.0, zoom=16)
    assert y_north < y_south


def test_higher_zoom_spreads_pixels_further_apart():
    x_low_zoom, _ = _lonlat_to_pixel(10.0, 56.0, zoom=10)
    x_high_zoom, _ = _lonlat_to_pixel(10.0, 56.0, zoom=16)
    # Same point, but the whole world map is larger at higher zoom.
    assert x_high_zoom > x_low_zoom


def test_world_origin_is_top_left():
    x, y = _lonlat_to_pixel(-180.0, 85.0, zoom=1)
    assert x == 0
    assert y < TILE_SIZE  # near the top, not exact due to Mercator's polar distortion
