from values import Size, Resistor, Capacitor, Inductor, Diode
from values import Size, CapacitorType, InductorType, InductorCoreType
from drawer import generate_label

generate_label(
    Resistor("100k", Size.SMD_I0603),
    Capacitor("10μ", Size.SMD_I0603),
    Inductor("1m", Size.SMD_I0805),
    Diode("1N4148", Size.THT_AXIAL),
)
