import ctypes
import os
import numpy as np
import platform

# Determine the library extension based on the OS
system = platform.system()
if system == "Windows":
    lib_ext = ".dll"
elif system == "Linux":
    lib_ext = ".so"
elif system == "Darwin":
    lib_ext = ".dylib"
else:
    lib_ext = ".so"

# Path to the compiled library
lib_path = os.path.join(os.path.dirname(__file__), f"analytics{lib_ext}")

_analytics_lib = None

def load_library():
    global _analytics_lib
    if _analytics_lib is not None:
        return _analytics_lib

    if not os.path.exists(lib_path):
        raise FileNotFoundError(
            f"C++ library not found at {lib_path}. "
            "Please compile 'analytics.cpp' to a shared library."
        )

    try:
        _analytics_lib = ctypes.CDLL(lib_path)

        # Define argument types for safety
        # void calculate_sma(const double* data, int length, int window, double* result)
        _analytics_lib.calculate_sma.argtypes = [
            ctypes.POINTER(ctypes.c_double),
            ctypes.c_int,
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_double)
        ]

        # void calculate_ema(const double* data, int length, int window, double* result)
        _analytics_lib.calculate_ema.argtypes = [
            ctypes.POINTER(ctypes.c_double),
            ctypes.c_int,
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_double)
        ]

        # void calculate_rsi(const double* data, int length, int window, double* result)
        _analytics_lib.calculate_rsi.argtypes = [
            ctypes.POINTER(ctypes.c_double),
            ctypes.c_int,
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_double)
        ]

        # void calculate_stddev(const double* data, int length, int window, double* result)
        _analytics_lib.calculate_stddev.argtypes = [
            ctypes.POINTER(ctypes.c_double),
            ctypes.c_int,
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_double)
        ]

        # void calculate_max_drawdown(const double* data, int length, double* result)
        _analytics_lib.calculate_max_drawdown.argtypes = [
            ctypes.POINTER(ctypes.c_double),
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_double)
        ]

        return _analytics_lib

    except Exception as e:
        # Re-raise the exception so the user knows why it failed
        raise RuntimeError(f"Failed to load C++ library at {lib_path}: {e}") from e

def _prepare_array(arr):
    arr = np.ascontiguousarray(arr, dtype=np.float64)
    return arr, arr.ctypes.data_as(ctypes.POINTER(ctypes.c_double))

def calculate_sma(data: np.ndarray, window: int) -> np.ndarray:
    lib = load_library()
    if lib is None:
        raise RuntimeError("C++ library not loaded")

    data_arr, data_ptr = _prepare_array(data)
    length = len(data_arr)
    result = np.zeros(length, dtype=np.float64)
    result_ptr = result.ctypes.data_as(ctypes.POINTER(ctypes.c_double))

    lib.calculate_sma(data_ptr, length, window, result_ptr)
    return result

def calculate_ema(data: np.ndarray, window: int) -> np.ndarray:
    lib = load_library()
    if lib is None:
        raise RuntimeError("C++ library not loaded")

    data_arr, data_ptr = _prepare_array(data)
    length = len(data_arr)
    result = np.zeros(length, dtype=np.float64)
    result_ptr = result.ctypes.data_as(ctypes.POINTER(ctypes.c_double))

    lib.calculate_ema(data_ptr, length, window, result_ptr)
    return result

def calculate_rsi(data: np.ndarray, window: int) -> np.ndarray:
    lib = load_library()
    if lib is None:
        raise RuntimeError("C++ library not loaded")

    data_arr, data_ptr = _prepare_array(data)
    length = len(data_arr)
    result = np.zeros(length, dtype=np.float64)
    result_ptr = result.ctypes.data_as(ctypes.POINTER(ctypes.c_double))

    lib.calculate_rsi(data_ptr, length, window, result_ptr)
    return result

def calculate_stddev(data: np.ndarray, window: int) -> np.ndarray:
    lib = load_library()
    if lib is None:
        raise RuntimeError("C++ library not loaded")

    data_arr, data_ptr = _prepare_array(data)
    length = len(data_arr)
    result = np.zeros(length, dtype=np.float64)
    result_ptr = result.ctypes.data_as(ctypes.POINTER(ctypes.c_double))

    lib.calculate_stddev(data_ptr, length, window, result_ptr)
    return result

def calculate_max_drawdown(data: np.ndarray) -> np.ndarray:
    lib = load_library()
    if lib is None:
        raise RuntimeError("C++ library not loaded")

    data_arr, data_ptr = _prepare_array(data)
    length = len(data_arr)
    result = np.zeros(length, dtype=np.float64)
    result_ptr = result.ctypes.data_as(ctypes.POINTER(ctypes.c_double))

    lib.calculate_max_drawdown(data_ptr, length, result_ptr)
    return result
