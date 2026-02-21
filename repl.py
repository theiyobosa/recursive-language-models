import contextlib, io, traceback
from typing import Dict



# BASE_CODE = """
# __final_answer__ = None

# def FINAL(answer):
#     global __final_answer__
#     __final_answer__ = answer

# def FINAL_VAR(variable_name):
#     global __final_answer__
#     __final_answer__ = globals()[variable_name]
# """



class REPL:
    def __init__(self):
        self.ns = {}
        # self.run_cell(BASE_CODE)


    def _clean_code(self, code: str) -> str:
        code_ = code.replace('```python', '').replace('```', '')
        return code_
    

    def reset_final_answer(self) -> None:
        # self.ns['__final_answer__'] = None
        self.ns["FINAL"] = None


    def run_cell(self, code: str) -> Dict:
        out, err = io.StringIO(), io.StringIO()
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code_ = self._clean_code(code)
                exec(code_, self.ns, self.ns)
            return {"ok": True, "stdout": out.getvalue(), "stderr": err.getvalue()}
        except Exception:
            return {
                "ok": False,
                "stdout": out.getvalue(),
                "stderr": err.getvalue(),
                "error": traceback.format_exc(),
            }
        

    @property
    def stall(self) -> Dict:
        stall = {k: v for k, v in self.ns.items() if k != '__builtins__'}
        return stall