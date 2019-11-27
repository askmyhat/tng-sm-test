These tests require the Emulator to have `enable_learning` parameter set to `True`.

```
# Set environment variable
export TANGOTEST_ENABLE_LEARNING=1

# The Emulator requires to be run as root
# Use -E flag to preserve environment variables
sudo -E pytest
```
