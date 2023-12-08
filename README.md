Used libraries:<br />
from cs50 import SQL<br />
from flask import Flask, flash, redirect, render_template, request, session, jsonify<br />
from flask_session import Session<br />
from tempfile import mkdtemp<br />
from werkzeug.security import check_password_hash, generate_password_hash<br />
from helpers import apology, login_required<br />

import requests<br />
import sqlite3 <br />
from datetime import datetime, timedelta <br />
