#include <vector>
#include <cmath>
#include <algorithm>
#include <numeric>

extern "C" {

    // 1. Simple Moving Average
    void calculate_sma(const double* data, int length, int window, double* result) {
        for (int i = 0; i < length; ++i) {
            if (i < window - 1) {
                result[i] = NAN; // Not enough data
            } else {
                double sum = 0.0;
                for (int j = 0; j < window; ++j) {
                    sum += data[i - j];
                }
                result[i] = sum / window;
            }
        }
    }

    // 2. Exponential Moving Average
    void calculate_ema(const double* data, int length, int window, double* result) {
        double multiplier = 2.0 / (window + 1);

        // Initialize first EMA with SMA
        double sum = 0.0;
        for (int i = 0; i < window; ++i) {
            sum += data[i];
        }
        double prev_ema = sum / window;

        for (int i = 0; i < length; ++i) {
            if (i < window - 1) {
                result[i] = NAN;
            } else if (i == window - 1) {
                result[i] = prev_ema;
            } else {
                double current_ema = (data[i] - prev_ema) * multiplier + prev_ema;
                result[i] = current_ema;
                prev_ema = current_ema;
            }
        }
    }

    // 3. Relative Strength Index (RSI)
    void calculate_rsi(const double* data, int length, int window, double* result) {
        if (length <= window) return;

        std::vector<double> gains(length, 0.0);
        std::vector<double> losses(length, 0.0);

        for (int i = 1; i < length; ++i) {
            double change = data[i] - data[i - 1];
            if (change > 0) {
                gains[i] = change;
            } else {
                losses[i] = -change;
            }
        }

        double avg_gain = 0.0;
        double avg_loss = 0.0;

        // First average
        for (int i = 1; i <= window; ++i) {
            avg_gain += gains[i];
            avg_loss += losses[i];
        }
        avg_gain /= window;
        avg_loss /= window;

        for (int i = 0; i < length; ++i) {
            if (i < window) {
                result[i] = NAN;
            } else {
                if (i > window) {
                    avg_gain = (avg_gain * (window - 1) + gains[i]) / window;
                    avg_loss = (avg_loss * (window - 1) + losses[i]) / window;
                }

                if (avg_loss == 0) {
                    result[i] = 100.0;
                } else {
                    double rs = avg_gain / avg_loss;
                    result[i] = 100.0 - (100.0 / (1.0 + rs));
                }
            }
        }
    }

    // 4. Rolling Standard Deviation (Volatility)
    void calculate_stddev(const double* data, int length, int window, double* result) {
        for (int i = 0; i < length; ++i) {
            if (i < window - 1) {
                result[i] = NAN;
            } else {
                double sum = 0.0;
                for (int j = 0; j < window; ++j) {
                    sum += data[i - j];
                }
                double mean = sum / window;

                double sq_sum = 0.0;
                for (int j = 0; j < window; ++j) {
                    double diff = data[i - j] - mean;
                    sq_sum += diff * diff;
                }
                result[i] = std::sqrt(sq_sum / (window - 1)); // Sample standard deviation
            }
        }
    }

    // 5. Maximum Drawdown (Running)
    void calculate_max_drawdown(const double* data, int length, double* result) {
        double peak = -1e9; // Initialize with a very small number

        for (int i = 0; i < length; ++i) {
            if (data[i] > peak) {
                peak = data[i];
            }

            if (peak != 0) {
                result[i] = (data[i] - peak) / peak;
            } else {
                result[i] = 0.0;
            }
        }
    }
}
