#!/bin/bash

TITLE="AllSky Image Annotater Installer"

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )



confirm() {
	if (whiptail --title "$TITLE" --yesno "Are you sure you wish to proceed with the installation?\n\n PLEASE ENSURE YOU HAVE BACKUP UP YOUR ALLSKY INSTALLATION" 10 78); then
		CONTINUE="YES"
	else
		CONTINUE="NO"
		exit 1
	fi
}

check_if_installed() {
    if [[ -f ${SAVE_SCRIPT} ]]; then
	    MODDED=`grep annotate.py ${SAVE_SCRIPT}`
    fi

	if [[ ! -z ${MODDED} ]]; then
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
	if [[ -z ${MODDED} ]]; then
       	if (whiptail --title "$TITLE" --yesno "Do you wish to automatically modify the allsky scripts to run the annotater?" 10 78); then
       	    AUTO="YES"
	    fi
	fi
}

check_and_install_config() {
	if [[ ! -f "../annotate.json" ]]; then
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

source "${ALLSKY_HOME}/variables.sh"
source "${SCRIPT_DIR}/installercommon.sh"
check_dir
check_allsky_Installed
check_allsky_not_running
check_allsky_type

ANNOTATE_SCRIPT="$(dirname ${PWD})/annotate.py"

check_if_installed
confirm

TERM=ansi # Fix a bug on some shells that prevents the infobox appearing
whiptail --title "$TITLE" --infobox "Checking and installing Dependencies. Please wait as this may take a few minutes" 8 78
#pip3 install --no-warn-script-location -r "${SCRIPT_DIR}/requirements.txt" 2>&1 > dependencies.log
#sudo apt-get -y install libatlas-base-dev 2>&1 >> dependencies.log
auto_modify

if [[ ${AUTO} == "YES" ]]; then
	DATE=`date`
	if [[ ${ALLSKYTYPE} == "OLD" ]]; then
        cp "${SAVE_SCRIPT}" "${SAVE_SCRIPT}-bak"
        cp "${SAVE_SCRIPT_DAY}" "${SAVE_SCRIPT_DAY}-bak"
		sed -i -e "s~${INSERT_ANNOTATER_BEFORE}~# Start AllSky Annotater\n# Run the image annotation script. Added by the annotater installer on ${DATE}\nif [[ -z \${IMAGE_PROCESSING_STAGE} || \${IMAGE_PROCESSING_STAGE} == \"POST\" ]]; then\n  if [[ -x \"${ANNOTATE_SCRIPT}\" ]]\nthen\n    ${ANNOTATE_SCRIPT} -k stage=\${IMAGE_PROCESSING_STAGE} daynight=\${IMAGE_DAY_OR_NIGHT} filename=\${IMAGE_FILE_NAME} cameratemp=\${IMAGE_TEMP} exposure=\${IMAGE_EXPOSURE}\n  fi\nfi\n# End AllSky Annotater\n\n${INSERT_ANNOTATER_BEFORE}~g" ${SAVE_SCRIPT}
		sed -i -e "s~${INSERT_ANNOTATER_BEFORE}~# Start AllSky Annotater\n# Run the image annotation script. Added by the annotater installer on ${DATE}\nif [[ -z \${IMAGE_PROCESSING_STAGE} || \${IMAGE_PROCESSING_STAGE} == \"POST\" ]]; then\n  if [[ -x \"${ANNOTATE_SCRIPT}\" ]]\nthen\n    ${ANNOTATE_SCRIPT} -k stage=\${IMAGE_PROCESSING_STAGE} daynight=\${IMAGE_DAY_OR_NIGHT} filename=\${IMAGE_FILE_NAME} cameratemp=\${IMAGE_TEMP} exposure=\${IMAGE_EXPOSURE}\n  fi\nfi\n# End AllSky Annotater\n\n${INSERT_ANNOTATER_BEFORE}~g" ${SAVE_SCRIPT_DAY}
	else 
		if [[ ! -f ${SAVE_SCRIPT} ]]; then
			cp "${SAVE_SCRIPT_REPO}" "${SAVE_SCRIPT}"
		fi
		echo "" >> ${SAVE_SCRIPT}
		echo "" >> ${SAVE_SCRIPT}
		echo "# Start AllSky Annotater" >> ${SAVE_SCRIPT}
		echo "# Run the image annotation script. Added by the annotater installer on ${DATE}" >> ${SAVE_SCRIPT}
		echo "if [[ -z \${IMAGE_PROCESSING_STAGE} || \${IMAGE_PROCESSING_STAGE} == \"POST\" ]]; then" >> ${SAVE_SCRIPT}
		echo "	if [[ -x \"${ANNOTATE_SCRIPT}\" ]]; then" >> ${SAVE_SCRIPT}
		echo "  		${ANNOTATE_SCRIPT} -k stage=\${IMAGE_PROCESSING_STAGE} daynight=\${IMAGE_DAY_OR_NIGHT} filename=\${IMAGE_FILE_NAME} cameratemp=\${IMAGE_TEMP} exposure=\${IMAGE_EXPOSURE}" >> ${SAVE_SCRIPT}
		echo "	fi" >> ${SAVE_SCRIPT}
		echo "fi" >> ${SAVE_SCRIPT}
		echo "# End AllSky Annotater" >> ${SAVE_SCRIPT}
		echo "" >> ${SAVE_SCRIPT}
		echo "" >> ${SAVE_SCRIPT}
	fi
fi

check_and_install_config

complete