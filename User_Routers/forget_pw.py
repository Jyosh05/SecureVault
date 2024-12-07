from flask import Blueprint, render_template, jsonify
from Utils.general_utils import mydb

forget_pw_bp = Blueprint('forget_pw', __name__, template_folder='templates')


@forget_pw_bp.route("forget_pw")
def forget_pw():
    return render_template()