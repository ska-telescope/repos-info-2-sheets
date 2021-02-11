#!/bin/bash

function gup() {
	current_branch=$(git branch 2> /dev/null | sed -e '/^[^*]/d' -e 's/* \(.*\)/\1/');
	git checkout master;
	git fetch;
	git pull;
	git checkout $current_branch;
	git diff master HEAD
	read -p "Are you sure you want to merge from master? Press \"y\" to merge, or Enter to cancel: " answer
	if [ "$answer" = "y" ]; then
		git merge master;
	fi;
}

