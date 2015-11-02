# androidWireshark

Use wireshark to dump network in Android Phone.



## Install

1. install **adb** at local computer

    ```
       cd install/adb
       ./ADB-Install-Mac.sh
    ```
    
2. install **tcpdump** to Android Phone.

    ```
    cd install/tcpdump
    ./install.sh
    ```

## Usage

```
./adb_wireshark.sh
```

**Problem:**

1. Launch **Wireshark** could fail or late. Just try again, and problem would be resolved.