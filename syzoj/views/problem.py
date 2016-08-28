from urllib import urlencode

from flask import jsonify, redirect, url_for, abort, request, render_template

from syzoj import oj, controller
from syzoj.models import User, Problem, File, FileParser
from syzoj.controller import Paginate, Tools
from .common import need_login, not_have_permission, show_error

def renderMarkdown(s):
    import subprocess
    process = subprocess.Popen('moemark-renderer',
                               stdin = subprocess.PIPE,
                               stdout = subprocess.PIPE,
                               stderr = subprocess.PIPE)
    stdoutdata, stderrdata = process.communicate(input = s)
    return stdoutdata

@oj.route("/problem")
def problem_set():
    query = Problem.query

    def make_url(page, other):
        return url_for("problem_set") + "?" + urlencode({"page": page})

    sorter = Paginate(query, make_url=make_url, cur_page=request.args.get("page"), edge_display_num=50, per_page=50)
    return render_template("problem_set.html", tool=Tools, tab="problem_set", sorter=sorter)


@oj.route("/problem/<int:problem_id>")
def problem(problem_id):
    user = User.get_cur_user()

    problem = Problem.query.filter_by(id=problem_id).first()
    if not problem:
        abort(404)

    if problem.is_allowed_use(user) == False:
        return not_have_permission()
    
    problem.description = renderMarkdown(problem.description);
    problem.input_format = renderMarkdown(problem.input_format);
    problem.output_format = renderMarkdown(problem.output_format);
    problem.example = renderMarkdown(problem.example);
    problem.limit_and_hint = renderMarkdown(problem.limit_and_hint);
    
    return render_template("problem.html", tool=Tools, tab="problem_set", problem=problem)


@oj.route("/problem/<int:problem_id>/edit", methods=["GET", "POST"])
def edit_problem(problem_id):
    user = User.get_cur_user()
    if not user:
        return need_login()

    problem = Problem.query.filter_by(id=problem_id).first()

    if request.method == "POST":
        if problem and problem.is_allowed_edit(user) == False:
            return not_have_permission()

        if not problem:
            problem_id = controller.create_problem(user=user, title=request.form.get("title"))
            problem = Problem.query.filter_by(id=problem_id).first()
        problem.update(title=request.form.get("title"),
                       description=request.form.get("description"),
                       input_format=request.form.get("input_format"),
                       output_format=request.form.get("output_format"),
                       example=request.form.get("example"),
                       limit_and_hint=request.form.get("limit_and_hint"))

        problem.save()

        return redirect(url_for("problem", problem_id=problem.id))
    else:
        return render_template("edit_problem.html", tool=Tools, problem=problem)


@oj.route("/problem/<int:problem_id>/upload", methods=["GET", "POST"])
def upload_testdata(problem_id):
    user = User.get_cur_user()
    if not user:
        return need_login()

    problem = Problem.query.filter_by(id=problem_id).first()
    if not problem:
        abort(404)
    if problem.is_allowed_edit(user) == False:
        return not_have_permission()
    if request.method == "POST":
        file = request.files.get("testdata")
        if file:
            problem.update_testdata(file)
        if request.form.get("time_limit"):
            problem.time_limit = int(request.form.get("time_limit"))
        if request.form.get("memory_limit"):
            problem.memory_limit = int(request.form.get("memory_limit"))
        io_method = request.form['io-method']
            
        if io_method == "std-io":
            problem.file_io = False
        elif request.form.get("time_limit") and request.form.get("time_limit"):
            problem.file_io = True
            problem.file_io_input_name = request.form.get("file-io-input-name")
            problem.file_io_output_name = request.form.get("file-io-output-name")
        else: 
            problem.file_io = False

        problem.save()
        return redirect(url_for("upload_testdata", problem_id=problem_id))
    else:
        return render_template("upload_testdata.html", tool=Tools, problem=problem, parse=FileParser.parse_as_testdata)


# TODO:Maybe need add the metho of toggle is_public attr to Problem
@oj.route("/api/problem/<int:problem_id>/public", methods=["POST", "DELETE"])
def change_public_attr(problem_id):
    session_id = request.args.get('session_id')
    user = User.get_cur_user(session_id=session_id)
    problem = Problem.query.filter_by(id=problem_id).first()
    if problem and user and user.is_admin:
        if request.method == "POST":
            problem.is_public = True
        elif request.method == "DELETE":
            problem.is_public = False
        problem.save()
    else:
        abort(404)
    return jsonify({"status": 0})
