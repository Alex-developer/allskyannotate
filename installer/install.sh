#!/bin/bash

TITLE="AllSky Image Annotater Installer"

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

source ${SCRIPT_DIR}/installercommon.sh

calc_wt_size() {
        # NOTE: it's tempting to redirect stderr to /dev/null, so supress error
        # output from tput. However in this case, tput detects neither stdout or
        # stderr is a tty and so only gives default 80, 24 values
        WT_HEIGHT=18
        WT_WIDTH=$(tput cols)

        if [ -z "$WT_WIDTH" ] || [ "$WT_WIDTH" -lt 60 ]; then
                WT_WIDTH=80
        fi
        if [ "$WT_WIDTH" -gt 178 ]; then
                WT_WIDTH=120
        fi
        WT_MENU_HEIGHT=$(($WT_HEIGHT-7))
}


confirm() {
	if (whiptail --title "$TITLE" --yesno "Are you sure you wish to proceed with the installation?\n\n PLEASE ENSURE YOU HAVE BACKUP UP YOUR ALLSKY INSTALLATION" 10 78); then
		CONTINUE="YES"
	else
		CONTINUE="NO"
		exit 1
	fi
}

check_installed() {
	MODDED=`grep annotate.py ${SAVE_SCRIPT}`
	if [ ! -z "$MODDED" ]; then
       		if (whiptail --title "$TITLE" --yesno "The annotater appears to be installed. Would you like to continue?" 10 78); then
       	        	GO="YES"
			else
				exit 1
	        fi
	fi
}

auto_modify() {
	AUTO="NO"
	MODDED=`grep annotate.py ${SAVE_SCRIPT}`
	if [ -z "$MODDED" ]; then
       		if (whiptail --title "$TITLE" --yesno "Do you wish to automatically modify the allsky scripts to run the annotater?" 10 78); then
       	        	AUTO="YES"
	        fi
	fi
}

check_allsky_Installed() {
	if [ -z "${ALLSKY_HOME}" ]; then
		whiptail --title "$TITLE" --msgbox "Unable to locate the AllSky software. Please ensure you are running this script as the same user that AllSky runs as, normally pi. The installation will now abort"  10 78
		exit 1
	fi
}

check_allsky_not_running() {
	ALLSKY_PID=`pgrep allsky.sh`
	if [ ! -z "$ALLSKY_PID" ]; then
		whiptail --title "$TITLE" --msgbox "The AllSky Software appears to be running, on pid ${ALLSKY_PID}. Please stop the Allsky software before attempting this installation"  10 78
		exit 1
	fi
}

check_and_install_config() {
	if [ ! -f "../annotate.json" ]; then
		if (whiptail --title "$TITLE" --yesno "No config file found would you like to see a basic list of configs and install one?" 10 78); then
			if file_select "Please, select a file" ../examples/configs "*.json" ; then
				cp ../examples/configs/$FILE_SELECTED ../annotate.json
			fi
		fi	
	fi
}

complete() {
	whiptail --title "$TITLE" --msgbox "Installation complete. Please restart the AllSky software or reboot your pi to continue"  10 78
}

function file_select
{
    local TITLE=${1:-$MSG_INFO_TITLE}
    local LOCAL_PATH=${2:-$(pwd)}
    local FILE_MASK=${3:-"*"}
    local FILES=()

    for FILE in $(find $LOCAL_PATH -maxdepth 1 -type f -name "$FILE_MASK" -printf "%f . " 2> /dev/null)
    do
        FILES+=($FILE)
    done

    FILE_SELECTED=$(whiptail --clear --backtitle "" --title "$TITLE" --menu "" 38 80 30 ${FILES[@]} 3>&1 1>&2 2>&3)
}

check_allsky_Installed
check_allsky_not_running
source "${ALLSKY_HOME}/variables.sh"
SAVE_SCRIPT="${ALLSKY_SCRIPTS}/saveImageNight.sh"
ANNOTATE_SCRIPT="$(dirname ${PWD})/annotate.py"
calc_wt_size
check_installed
confirm

TERM=ansi # Fix a bug on some shells that prevents the infobox appearing
whiptail --title "$TITLE" --infobox "Checking and installing Dependencies. Please wait as this may take a few minutes" 8 78
pip3 install -r "${SCRIPT_DIR}/requirements.txt" 2>&1 > dependencies.log
sudo apt-get install libatlas-base-dev 2>&1 >> dependencies.log
auto_modify

if [ "$AUTO" = "YES" ]; then
	DATE=`date`
        cp "${SAVE_SCRIPT}" "${ALLSKY_SCRIPTS}/saveImageNight.sh-bak"
	sed -i -e "s~${INSERT_ANNOTATER_BEFORE}~\n# Run the image annotation script. Added by the annotater installer on ${DATE}\nif [[ -x \"${ANNOTATE_SCRIPT}\" ]]\nthen\n  ${ANNOTATE_SCRIPT}\nfi\n\n\n# Copy image to the final location.~g" ${ALLSKY_SCRIPTS}/saveImageNight.sh
fi

check_and_install_config

complete
