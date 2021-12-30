#!/bin/bash

TITLE="AllSky Image Annotater Un Installer"
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

check_allsky_not_running() {
	ALLSKY_PID=`pgrep allsky.sh`
	if [[ ! -z ${ALLSKY_PID} ]]; then
		whiptail --title "$TITLE" --msgbox "The AllSky Software appears to be running, on pid ${ALLSKY_PID}. Please stop the Allsky software before attempting to uninstall"  10 78
		exit 1
	fi
}

confirm() {
	if (whiptail --title "$TITLE" --yesno "Are you sure you wish to proceed with the Un installation?" 10 78); then
		CONTINUE="YES"
	else
		CONTINUE="NO"
		exit 1
	fi
}

complete() {
    whiptail --title "$TITLE" --msgbox "The annotater has been removed from the allsky software" 10 78
}

source "${ALLSKY_HOME}/variables.sh"
source "${SCRIPT_DIR}/installercommon.sh"
check_dir
check_allsky_Installed
check_allsky_not_running
SAVE_SCRIPT="${ALLSKY_SCRIPTS}/saveImageNight.sh"
ANNOTATE_SCRIPT="$(dirname ${PWD})/annotate.py"
check_allsky_type
check_installed
confirm

sed -i '/# Start AllSky Annotater/,/# End AllSky Annotater/d' ${SAVE_SCRIPT}
if [[ ${ALLSKYTYPE} == "OLD" ]]; then
	sed -i '/# Start AllSky Annotater/,/# End AllSky Annotater/d' ${SAVE_SCRIPT_DAY}
fi

complete