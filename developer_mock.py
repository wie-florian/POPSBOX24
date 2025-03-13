import platform

# Determine if script is running on a Linux system
IS_LINUX = platform.system() == "Linux"

# Necessary platform-specific imports
if IS_LINUX:
    import RPi.GPIO as GPIO
    from sensirion_i2c_driver import I2cConnection, LinuxI2cTransceiver
    from sensirion_i2c_sen5x import Sen5xI2cDevice
    import adafruit_bme680
    import adafruit_ccs811
    import busio
    import serial
    import lcddriver
    import udp_pops
    from SIM7600_GPS import SIM7600
else:
    # Define mock classes for non-Linux environments
    class MockGPIO:
        BCM = "BCM"
        OUT = "OUT"
        IN = "IN"
        PUD_DOWN = "PUD_DOWN"
        HIGH = "HIGH"
        LOW = "LOW"
        RISING = "RISING"

        @staticmethod
        def setup(pin, mode, pull_up_down=None):
            print(f"MockGPIO: Configured pin {pin}, mode {mode}, pull={pull_up_down}")

        @staticmethod
        def output(pin, state):
            print(f"MockGPIO: Set pin {pin} to {'HIGH' if state == MockGPIO.HIGH else 'LOW'}")

        @staticmethod
        def add_event_detect(pin, edge, callback=None):
            print(f"MockGPIO: Event detection added for pin {pin} on edge {edge}")


    class MockI2CConnection:
        def __init__(self, *args, **kwargs):
            print("MockI2CConnection initialized.")


    class MockLinuxI2cTransceiver:
        def __init__(self, device):
            self.device = device
            print(f"MockLinuxI2cTransceiver initialized for device {device}")

        def __enter__(self):
            print("MockLinuxI2cTransceiver entered.")
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            print("MockLinuxI2cTransceiver exited.")


    class MockValue:
        def __init__(self, available, value, scaled=None):
            self.available = available
            self.value = value
            self.scaled = scaled  # Add a 'scaled' attribute, with a default of None


    class MockHumidity:
        def __init__(self, percent_rh):
            self.percent_rh = percent_rh  # Mimic the real humidity object


    class MockTemperature:
        def __init__(self, degrees_celsius):
            self.degrees_celsius = degrees_celsius  # Updated to match the original code


    class MockPhysicalValue:
        def __init__(self, physical):
            self.physical = physical  # Represents the real "physical" attribute


    class MockMeasuredValues:
        def __init__(self):
            # Replace integers with MockPhysicalValue objects for mass concentrations
            self.mass_concentration_1p0 = MockPhysicalValue(10)
            self.mass_concentration_2p5 = MockPhysicalValue(20)
            self.mass_concentration_4p0 = MockPhysicalValue(30)
            self.mass_concentration_10p0 = MockPhysicalValue(40)

            # Return specific mocks for humidity and temperature
            self.ambient_humidity = MockHumidity(53.2)  # Provide the expected percent_rh
            self.ambient_temperature = MockTemperature(22.1)  # Provide the expected degrees_celsius

            # VOC and NOx indices remain unchanged
            self.voc_index = MockValue(available=True, value=0.8)
            self.nox_index = MockValue(available=True, value=0.3)


    class MockSen5xI2cDevice:
        def __init__(self, connection):
            print(f"MockSen5xI2cDevice initialized with connection: {connection}")

        def device_reset(self):
            print("MockSen5xI2cDevice: Device reset")

        def start_measurement(self):
            print("MockSen5xI2cDevice: Measurement started.")

        def read_measured_values(self):
            # Return an object with attributes instead of a dictionary
            return MockMeasuredValues()


    class MockAdafruitBME680:
        class Adafruit_BME680_I2C:
            def __init__(self, i2c, address=0x76):
                self.i2c = i2c
                self.address = address
                print(f"MockAdafruitBME680_I2C initialized with i2c={i2c} and address={hex(address)}")
                self._temperature = 25.0  # Mock temperature in °C
                self._humidity = 50.0  # Mock humidity in %
                self._pressure = 1013.25  # Mock pressure in hPa
                self._gas_resistance = 1200  # Mock gas resistance in ohms

            @property
            def temperature(self):
                print("MockAdafruitBME680: Returning mock temperature")
                return self._temperature

            @property
            def humidity(self):
                print("MockAdafruitBME680: Returning mock humidity")
                return self._humidity

            @property
            def pressure(self):
                print("MockAdafruitBME680: Returning mock pressure")
                return self._pressure

            @property
            def gas(self):
                print("MockAdafruitBME680: Returning mock gas resistance")
                return self._gas_resistance


    class MockAdafruitCCS811:
        def __init__(self, i2c):
            """Initialize with an instance of the mocked CCS811 sensor."""
            self._eco2 = 400  # Default CO2 level in ppm (parts per million)
            self._tvoc = 5  # Default TVOC level in ppb (parts per billion)
            self._data_ready = True  # Internal flag to simulate data readiness

        @property
        def eco2(self):
            """Return equivalent CO2 concentration in ppm."""
            if self._data_ready:
                return self._eco2
            else:
                raise Exception("Data not ready!")

        @property
        def tvoc(self):
            """Return total volatile organic compounds concentration in ppb."""
            if self._data_ready:
                return self._tvoc
            else:
                raise Exception("Data not ready!")

        @property
        def data_ready(self):
            """Simulated 'data_ready' flag to represent sensor readiness."""
            return self._data_ready

        def simulate_data_ready(self, eco2, tvoc):
            """Simulate the sensor being ready and update the CO2 and TVOC values."""
            self._eco2 = eco2
            self._tvoc = tvoc
            self._data_ready = True

        class CCS811:
            def __init__(self, i2c):
                """Mock initialization of the CCS811 sensor."""
                self._data_ready = True  # Internal flag to simulate data readiness
                self.i2c = i2c

            @property
            def data_ready(self):
                return self._data_ready

            def simulate_data_ready(self):
                """Method to simulate the sensor reporting that data is ready."""
                self._data_ready = True

    class MockBusIO:
        class I2C:
            def __init__(self, scl, sda):
                self.scl = scl
                self.sda = sda
                print(f"MockBusIO.I2C initialized with SCL={scl} and SDA={sda}")

            def scan(self):
                print("MockBusIO.I2C: Scanning for devices...")
                return [0x76, 0x5A]  # Mock I2C device addresses (e.g., BME680, SGP30, etc.)


    class MockLCDDriver:
        def __init__(self):
            print("MockLCD Initialized")

        def lcd(self):
            return self  # Return self to mimic the real behavior of lcddriver.lcd()

        def lcd_clear(self):
            print("MockLCD: Cleared")

        def lcd_display_string(self, string, line):
            print(f"MockLCD[{line}]: {string}")


    class MockSIM7600GPS:
        def __init__(self):
            self.powered_on = False
            self.power_key = "mock_key"  # Placeholder for power_key
            print("MockSIM7600GPS initialized")

        def power_on(self, key):
            self.powered_on = True
            print(f"MockSIM7600GPS: Power ON using key {key}")

        def power_down(self, key):
            self.powered_on = False
            print(f"MockSIM7600GPS: Power OFF using key {key}")

        def send_at(self, command, response, timeout):
            print(f"MockSIM7600GPS AT Command Sent: {command}, expecting {response}")
            if "+CGPSINFO" in command:
                # Return valid GPS data with at least 9 fields
                return "OK", "+CGPSINFO: 1234.56,N,12345.67,W,180423,135000.0,100.5,50.0,1.5"
            return "OK", response


    class MockUDPPops:
        @staticmethod
        def init():
            print("MockUDPPops initialized.")

        @staticmethod
        def getPOPS():
            # Ensure the data simulates a real UDP response.
            # Each value corresponds to the indexes used in cleanPopsData:
            return ",".join([
                "mock_rnd1",  # rnd1 (index 0)
                "mock_rnd2",  # rnd2 (index 1)
                "/mock/path/to/data",  # path (index 2)
                "2023-10-01T12:00:00",  # datetime (index 3)
                "mock_rnd",  # rnd (index 4, not used in the function)
                "active",  # status (index 5)
                "good",  # data_status (index 6)
                "12345",  # part_ct (index 7)
                "45678",  # hist_sum (index 8)
                "78901",  # part_con (index 9)
                "10",  # bl (index 10)
                "20",  # blth (index 11)
                "0.15",  # std (index 12)
                "0.30",  # max_std (index 13)
                "1.00",  # p (index 14)
                "1.01",  # tof_p (index 15)
                "5000",  # pump_life (index 16)
                "25.0",  # width_std (index 17)
                "50.0",  # ave_width (index 18)
                "2.5",  # pops_flow (index 19)
                "1.2",  # pump_fb (index 20)
                "30.0",  # ld_temp (index 21)
                "1.5",  # laser_fb (index 22)
                "1.0",  # ld_mon (index 23)
                "22.3",  # temp (index 24)
                "3.7",  # batV (index 25)
                "1.8",  # laser_current (index 26)
                "2.0",  # flow_set (index 27)
                "12",  # bl_start (index 28)
                "1.5",  # th_mult (index 29)
                "16",  # nbins (index 30)
                "0.10",  # logmin (index 31)
                "10.0",  # logmax (index 32)
                "0",  # skip_save (index 33)
                "3",  # min_peak_pts (index 34)
                "7",  # max_peak_pts (index 35)
                "100",  # raw_pts (index 36)
                *[f"bin_{i}" for i in range(16)],  # b0 to b15 (indexes 37 to 52)
            ])

    # Assign mocks in place of real libraries
    GPIO = MockGPIO
    busio = MockBusIO
    I2cConnection = MockI2CConnection
    LinuxI2cTransceiver = MockLinuxI2cTransceiver
    Sen5xI2cDevice = MockSen5xI2cDevice
    adafruit_bme680 = MockAdafruitBME680
    adafruit_ccs811 = MockAdafruitCCS811
    lcddriver = MockLCDDriver()
    udp_pops = MockUDPPops
    SIM7600_GPS = MockSIM7600GPS()


# Helper functions to initialize sensors and modules
class MockEnvironment:
    def __init__(self):
        self.GPIO = GPIO
        self.busio = busio
        self.I2cConnection = I2cConnection
        self.LinuxI2cTransceiver = LinuxI2cTransceiver
        self.Sen5xI2cDevice = Sen5xI2cDevice
        self.adafruit_bme680 = adafruit_bme680()
        self.adafruit_ccs811 = adafruit_ccs811()
        self.lcddriver = lcddriver
        self.udp_pops = udp_pops
        self.SIM7600_GPS = SIM7600_GPS

    def initialize(self):
        print("MockEnvironment: Initialization complete.")
        return {
            "GPIO": self.GPIO,
            "busio": self.busio,
            "I2cConnection": self.I2cConnection,
            "LinuxI2cTransceiver": self.LinuxI2cTransceiver,
            "Sen5xI2cDevice": self.Sen5xI2cDevice,
            "adafruit_bme680": self.adafruit_bme680,
            "adafruit_ccs811": self.adafruit_ccs811,
            "lcddriver": self.lcddriver,
            "udp_pops": self.udp_pops,
            "SIM7600_GPS": self.SIM7600_GPS,
        }


# Define what will be imported when using `from developer_mock import *`
__all__ = [
    "IS_LINUX",
    "GPIO",
    "busio",
    "I2cConnection",
    "LinuxI2cTransceiver",
    "Sen5xI2cDevice",
    "adafruit_bme680",
    "adafruit_ccs811",
    "lcddriver",
    "udp_pops",
    "SIM7600_GPS",
    "MockEnvironment",
]
