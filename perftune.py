#!/bin/bash

set -e

# Check if the script is being run as root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 
   exit 1
fi

# Install required tools
echo "Installing required tools..."
apt update
apt install -y nvidia-settings lm-sensors cpufrequtils

# Overclocking presets
declare -A presets
presets=( ["low"]="50 200" ["medium"]="100 400" ["high"]="150 600" )

# Custom profiles
profile_file="overclock_profiles.txt"

function load_profiles() {
    if [ -e "$profile_file" ]; then
        while read -r line; do
            name=$(echo $line | cut -d'|' -f1)
            gpu_offset=$(echo $line | cut -d'|' -f2)
            mem_offset=$(echo $line | cut -d'|' -f3)
            presets["$name"]="$gpu_offset $mem_offset"
        done < "$profile_file"
    fi
}

function save_profile() {
    echo "Enter profile name:"
    read profile_name
    echo "$profile_name|$gpu_offset|$mem_offset" >> "$profile_file"
    echo "Profile saved."
}

load_profiles

# Menu function
function menu() {
    clear
    echo "Performance Tuning Menu"
    echo "======================="
    echo "1. Display GPU information"
    echo "2. Display CPU information"
    echo "3. Overclock GPU"
    echo "4. Overclock CPU"
    echo "5. Reset GPU settings"
    echo "6. Adjust GPU power limit"
    echo "7. Enable/disable GPU persistence mode"
    echo "8. Set CPU governor"
    echo "9. Enable/disable hugepages"
    echo "10. Set I/O scheduler"
    echo "11. Exit"
    echo "Enter your choice:"
    read choice
}

# Functions for each menu option
function display_gpu_info() {
    nvidia-smi
}

function display_cpu_info() {
    lscpu
    sensors
}

function overclock_gpu() {
    echo "Enter GPU Clock Offset (MHz):"
    read gpu_offset
    echo "Enter Memory Clock Offset (MHz):"
    read mem_offset
    echo "Setting GPU and Memory Clock Offsets..."
    nvidia-settings -a "[gpu:0]/GPUGraphicsClockOffset[3]=$gpu_offset" -a "[gpu:0]/GPUMemoryTransferRateOffset[3]=$mem_offset"
    echo "Overclocking successful."
}

function overclock_cpu_advanced() {
    echo "WARNING: This operation may cause system instability and void your warranty. Proceed at your own risk."
    echo "Enter the desired CPU multiplier (e.g., 40 for 4.0 GHz, or 45 for 4.5 GHz):"
    read cpu_multiplier
    for cpu in /dev/cpu/[0-9]*; do
        wrmsr -p "$(basename $cpu)" 0x194 0x$(printf "%X" $((cpu_multiplier << 8)))
    done
    echo "CPU multiplier set to $cpu_multiplier."
    read -p "Press enter to continue..."
}

function overclock_memory() {
    echo "WARNING: This operation may cause system instability and void your warranty. Proceed at your own risk."
    echo "Enter the desired memory clock speed in MHz (e.g., 3200):"
    read mem_clock
    numactl --interleave=all --membind=0 --physcpubind=0-$(($(nproc)-1)) --localalloc taskset -c 0-$(($(nproc)-1)) dmidecode -t memory | grep -i "speed" | sed "s/Speed: //g" | awk '{if ($1 < '$mem_clock') print "Warning: The desired memory clock speed ("'$mem_clock'" MHz) exceeds the maximum supported speed for at least one memory module."}'
    echo "Memory overclocking is not supported directly through this script. Please follow your motherboard's documentation and adjust memory settings through BIOS/UEFI."
    read -p "Press enter to continue..."
}

function reset_gpu_settings() {
    nvidia-settings -a "[gpu:0]/GPUGraphicsClockOffset[3]=0" -a "[gpu:0]/GPUMemoryTransferRateOffset[3]=0"
    echo "GPU settings have been reset."
}

function adjust_gpu_power_limit() {
    echo "Enter GPU power limit in watts (e.g., 250):"
    read power_limit
    nvidia-smi -pl $power_limit
    echo "GPU power limit set to $power_limit watts."
    read -p "Press enter to continue..."
}

function toggle_gpu_persistence_mode() {
    echo "Enable persistence mode? (y/n):"
    read enable_pm
    if [[ $enable_pm == "y" ]]; then
        nvidia-smi -pm 1
        echo "Persistence mode enabled."
    else
        nvidia-smi -pm 0
        echo "Persistence mode disabled."
    fi
    read -p "Press enter to continue..."
}

function set_cpu_governor() {
    echo "Select CPU governor:"
    select governor in "performance" "powersave" "ondemand" "conservative"; do
        cpufreq-set -r -g $governor
        echo "CPU governor set to $governor."
        read -p "Press enter to continue..."
        break
    done
}

function toggle_hugepages() {
    echo "Enable hugepages? (y/n):"
    read enable_hp
    if [[ $enable_hp == "y" ]]; then
        echo "Enter the number of hugepages:"
        read num_hugepages
        echo "Setting up hugepages..."
        sysctl -w vm.nr_hugepages=$num_hugepages
        echo "Hugepages enabled with $num_hugepages pages."
    else
        sysctl -w vm.nr_hugepages=0
        echo "Hugepages disabled."
    fi
    read -p "Press enter to continue..."
}

function adjust_gpu_application_clocks() {
    echo "Select a preset for GPU application clocks:"
    select preset in "low" "medium" "high" "custom"; do
        case $preset in
            low)
                core_clock="600"
                mem_clock="1100"
                break
                ;;
            medium)
                core_clock="900"
                mem_clock="1300"
                break
                ;;
            high)
                core_clock="1200"
                mem_clock="1500"
                break
                ;;
            custom)
                echo "Enter desired core clock (in MHz):"
                read core_clock
                echo "Enter desired memory clock (in MHz):"
                read mem_clock
                break
                ;;
        esac
    done
    nvidia-settings -a "[gpu:0]/GPUGraphicsClockOffset[3]=$core_clock" -a "[gpu:0]/GPUMemoryTransferRateOffset[3]=$mem_clock"
    echo "GPU application clocks set to Core: $core_clock MHz, Memory: $mem_clock MHz."
    read -p "Press enter to continue..."
}

function set_swappiness() {
    echo "Enter desired swappiness value (0-100):"
    read swappiness
    sysctl -w vm.swappiness=$swappiness
    echo "Swappiness value set to $swappiness."
    read -p "Press enter to continue..."
}

function optimize_disk_cache_pressure() {
    echo "Enter desired disk cache pressure value (0-100):"
    read cache_pressure
    sysctl -w vm.vfs_cache_pressure=$cache_pressure
    echo "Disk cache pressure value set to $cache_pressure."
    read -p "Press enter to continue..."
}

function configure_thp() {
    echo "Select THP mode:"
    select mode in "always" "madvise" "never"; do
        echo $mode > /sys/kernel/mm/transparent_hugepage/enabled
        echo "Transparent Huge Pages mode set to $mode."
        read -p "Press enter to continue..."
        break
    done
}

function optimize_readahead() {
    echo "Enter desired readahead value (in kilobytes):"
    read readahead_kb
    blockdev --setra $readahead_kb /dev/sda
    echo "Readahead value set to $readahead_kb KB."
    read -p "Press enter to continue..."
}

function set_io_scheduler() {
    echo "Select I/O scheduler:"
    select io_scheduler in "noop" "deadline" "cfq" "bfq" "mq-deadline" "kyber"; do
        for device in /sys/block/sd*; do
            echo $io_scheduler > $device/queue/scheduler
        done
        echo "I/O scheduler set to $io_scheduler."
        read -p "Press enter to continue..."
        break
    done
}


