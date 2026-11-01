@echo off
cd /d %~dp0..
py generator\generate_data.py --profile full --output data\full
