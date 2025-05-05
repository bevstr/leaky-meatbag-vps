from flask import Blueprint, render_template

styleguide_bp = Blueprint('styleguide', __name__)

@styleguide_bp.route('/styleguide')
def styleguide():
    return render_template('styleguide.html')
