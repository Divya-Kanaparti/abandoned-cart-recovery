@echo off
cd /d %~dp0..
py generator\validation.py --input data\starter --output data\starter\validation
