@echo off
cd /d %~dp0..
py generator\generate_data.py --profile starter --output data\starter
