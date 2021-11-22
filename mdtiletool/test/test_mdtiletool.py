import pytest
import mdtiletool

def test_rbg_to_genesis_vdp():
    """Test the input and output of the conversion function"""
    assert mdtiletool.rgb_to_megadrive_vdp(255,255,255) == 0x0EEE

    assert mdtiletool.rgb_to_megadrive_vdp(0,0,0) == 0x000

def test_rbg_to_genesis_vdp_value_exception():
    """Test that a ValueError exception is thrown when a RGB value is not 0 - 255"""

    # RED too big
    with pytest.raises(ValueError):
        mdtiletool.rgb_to_megadrive_vdp(256,255,255)

    # GREEN too big
    with pytest.raises(ValueError):
        mdtiletool.rgb_to_megadrive_vdp(255,256,255)

    # BLUE too big
    with pytest.raises(ValueError):
        mdtiletool.rgb_to_megadrive_vdp(255,255,256)

    # RED too small
    with pytest.raises(ValueError):
        mdtiletool.rgb_to_megadrive_vdp(-1,255,255)

    # GREEN too small
    with pytest.raises(ValueError):
        mdtiletool.rgb_to_megadrive_vdp(256,-1,255)

    # BLUE too small
    with pytest.raises(ValueError):
        mdtiletool.rgb_to_megadrive_vdp(256,255,-1)
