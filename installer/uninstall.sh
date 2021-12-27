#!/bin/bash

TITLE="AllSky Image Annotater Un Installer"
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
source ${SCRIPT_DIR}/installercommon.sh

check_allsky_Installed() {
	if [ -z "${ALLSKY_HOME}" ]; then
		whiptail --title "$TITLE" --msgbox "Unable to locate the AllSky software. Please ensure you are running this script as the same user that AllSky runs as, normally pi. The installation will now abort"  10 78
		exit 1
	fi
}

check_installed() {
	MODDED=`grep annotate.py ${SAVE_SCRIPT}`
	if [ -z "$MODDED" ]; then
       	whiptail --title "$TITLE" --msgbox "The annotater is not installed. Press Ok to abort the uninstaller" 10 78
		exit 1
	fi
}

check_allsky_not_running() {
	ALLSKY_PID=`pgrep allsky.sh`
	if [ ! -z "$ALLSKY_PID" ]; then
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

check_have_backup() {
    BACKUPFULLPATH="${ALLSKY_HOME}/scripts/${BACKUPSCRIPT}"
    if [ ! -f ${BACKUPFULLPATH} ]; then
        whiptail --title "$TITLE" --msgbox "Cannot locate the ${BACKUPSCRIPT} file. Unable to Un Install automatically. Please remove the annotate.py code manually from the ${SCRIPT} script" 10 78
		exit 1
    fi
}

complete() {
    whiptail --title "$TITLE" --msgbox "The annotater has been removed from the allsky software" 10 78
}

check_allsky_Installed
check_allsky_not_running
source "${ALLSKY_HOME}/variables.sh"
SAVE_SCRIPT="${ALLSKY_SCRIPTS}/saveImageNight.sh"
ANNOTATE_SCRIPT="${PWD}/annotate.py"
check_have_backup
confirm

cp "${ALLSKY_HOME}/scripts/${BACKUPSCRIPT}" "${ALLSKY_HOME}/scripts/${SCRIPT}"
rm "${ALLSKY_HOME}/scripts/${BACKUPSCRIPT}"

complete