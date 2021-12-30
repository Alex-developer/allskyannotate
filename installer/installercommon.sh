#!/bin/bash

INSERT_ANNOTATER_BEFORE="# IMG_DIR and IMG_PREFIX are in config.sh"
TITLE="AllSky Image Annotater Installer"

check_dir() {
	INSTALLRUNDIR=${PWD##*/} 

	if [[ ${INSTALLRUNDIR} != "installer" ]]; then
		whiptail --title "$TITLE" --msgbox "Please run the installer from the installer directory"  10 78
		exit 1
	fi
}

check_allsky_not_running() {
	ALLSKY_PID=`pgrep allsky.sh`
	if [[ ! -z ${ALLSKY_PID} ]]; then
		whiptail --title "$TITLE" --msgbox "The AllSky Software appears to be running, on pid ${ALLSKY_PID}. Please stop the Allsky software before attempting this installation"  10 78
		exit 1
	fi
}

check_allsky_Installed() {
	if [[ -z ${ALLSKY_HOME} ]]; then
		whiptail --title "$TITLE" --msgbox "Unable to locate the AllSky software. Please ensure you are running this script as the same user that AllSky runs as, normally pi. The installation will now abort"  10 78
		exit 1
	fi
}

check_allsky_type() {
	if [[ -f "${ALLSKY_SCRIPTS}/saveImage_additionalSteps.sh" ]] || [[ -f "${ALLSKY_SCRIPTS}/saveImage_additionalSteps.repo" ]]; then
		ALLSKYTYPE="NEW"
		SAVE_SCRIPT="${ALLSKY_SCRIPTS}/saveImage_additionalSteps.sh"
		SAVE_SCRIPT_REPO="${ALLSKY_SCRIPTS}/saveImage_additionalSteps.repo"	
	else
		ALLSKYTYPE="OLD"
		SAVE_SCRIPT="${ALLSKY_SCRIPTS}/saveImageNight.sh"
		SAVE_SCRIPT_DAY="${ALLSKY_SCRIPTS}/saveImageDay.sh"
		SAVE_SCRIPT_REPO=""
	fi
}

check_installed() {
    if [[ -f ${SAVE_SCRIPT} ]]; then
	    MODDED=`grep annotate.py ${SAVE_SCRIPT}`
    fi

	if [[ -z ${MODDED} ]]; then
       	whiptail --title "$TITLE" --msgbox "The annotater is not installed. Press Ok to abort the uninstaller" 10 78
		exit 1
	fi
}