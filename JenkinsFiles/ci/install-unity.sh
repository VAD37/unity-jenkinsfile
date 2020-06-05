#!/usr/bin/env bash
set -e -x

BASEDIR=$(dirname "$0")
echo "$BASEDIR/source-config.sh"
. "$BASEDIR/source-config.sh"


# Unity Hub only work in unix shell
echo UNTIYHUB LOCATION: $UNITYHUB
echo UNITY VERSION: $UNITY_VERSION
echo UNITY CHANGESET: $UNITY_CHANGESET
echo UNITY MODULE: $UNITY_MODULE


# unityhub always return failure on CLI
installation=" \"$UNITYHUB\" -- --headless install --version $UNITY_VERSION --changeset $UNITY_CHANGESET --module $UNITY_MODULE"
eval $installation

echo end call


# Documentation: documentation
# Standard Assets: standardassets
# Example Project: example
# Android Build Support: android
# iOS Build Support: ios
# tvOS Build Support: appletv
# Linux Build Support: linux
# SamsungTV Build Support: samsung
# Tizen Build Support: tizen
# WebGL Build Support: webgl
# Windows Build Support: windows
# Facebook Gameroom Build Support: facebook-games
# MonoDevelop / Unity Debugger: monodevelop
# Vuforia Augmented Reality Support: vuforia-ar
# Language packs: language-ja, language-ko, language-zh-cn, language-zh-hant, language-zh-hans
# Mac Build Support (IL2CPP): mac-il2cpp
# Windows Build Support (Mono): windows-mono
# Android SDK & NDK Tools: android-sdk-ndk-tools
# Lumin OS (Magic Leap) Build Suppor: lumin
