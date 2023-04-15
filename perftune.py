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
    # ... (Overclock GPU function as in the previous revision)
}

function overclock_cpu() {
    # ... (Overclock CPU function as in the previous revision)
}

function reset_gpu_settings() {
    # ... (Reset GPU settings function as in the previous revision)
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

# Main loop for the menu
while true; do
    menu
    case $choice in
        1)
            display_gpu_info
            read -p "Press enter to continue..."
        ;;
        2)
            display_cpu_info
            read -p "Press enter to continue..."
        ;;
        3)
            overclock_gpu
        ;;
        4)
            overclock_cpu
        ;;
        5)
            reset_gpu_settings
        ;;
        6)
            adjust_gpu_power_limit
        ;;
        7)
            toggle_gpu_persistence_mode
        ;;
        8)
            set_cpu_governor
        ;;
        9)
            toggle_hugepages
        ;;
        10)
            set_io_scheduler
        ;;
        11)
            echo "Exiting..."
            exit 0
        ;;
        *)
            echo "Invalid choice, try again."
            read -p "Press enter to continue..."
        ;;
    esac
done

