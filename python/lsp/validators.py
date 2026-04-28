"""Shared catalog-validation helpers used by completion, diagnostics, and
code actions.

Every helper that touches a CATA object is defensive: the upstream
catalog has known quirks (callable `sd_prod` that throw on
introspection, type fields that aren't classes, BLOC.isEnabled that
raise on partial context). Each helper degrades to a benign default on
any exception.
"""

from __future__ import annotations

import inspect
import re
import sys


def _is_factor(kwd) -> bool:
    return "FactorKeyword" in type(kwd).__name__


def _is_bloc(kwd) -> bool:
    return "Bloc" in type(kwd).__name__


def find_keyword(definition, name: str, context):
    """Walk the keyword tree (descending into BLOCs and FACTs) and return
    the first keyword whose key matches `name`. BLOC branches that are
    disabled by `context` are skipped so a keyword only reachable via an
    inactive branch is not returned when a context is known."""
    try:
        for key, kwd in definition.items():
            if not hasattr(kwd, "definition"):
                continue
            if _is_bloc(kwd):
                if context is not None:
                    try:
                        if not kwd.isEnabled(context):
                            continue
                    except Exception:
                        pass
                found = find_keyword(kwd.definition, name, context)
                if found is not None:
                    return found
                continue
            if key == name:
                return kwd
            if _is_factor(kwd):
                found = find_keyword(kwd.definition, name, context)
                if found is not None:
                    return found
    except Exception:
        return None
    return None


def visible_keywords(definition, context):
    """Yield (name, kwd) pairs for keywords visible at this scope, with
    BLOC filtering when `context` is known."""
    try:
        for key, kwd in definition.items():
            if not hasattr(kwd, "definition"):
                continue
            if _is_bloc(kwd):
                if context is not None:
                    try:
                        if not kwd.isEnabled(context):
                            continue
                    except Exception:
                        pass
                yield from visible_keywords(kwd.definition, context)
                continue
            yield (key, kwd)
    except Exception:
        return


def required_keywords(definition, context):
    """Yield names of required keywords visible at this scope."""
    for name, kwd in visible_keywords(definition, context):
        try:
            if kwd.definition.get("statut") == "o":
                yield name
        except Exception:
            continue


def simp_defaults(definition) -> dict:
    """Collect ``{name: defaut}`` for top-level SIMP keywords that declare a
    `defaut`. Used to seed BLOC-evaluation context with values the user
    didn't type but the catalog assumes."""
    out: dict = {}
    try:
        for key, kwd in definition.items():
            if not hasattr(kwd, "definition"):
                continue
            if _is_bloc(kwd) or _is_factor(kwd):
                continue
            try:
                d = kwd.definition.get("defaut")
            except Exception:
                d = None
            if d is not None:
                out[key] = d
    except Exception:
        return out
    return out


def find_param(params: list[dict], name: str) -> dict | None:
    """Find a parsed-param dict (the shape produced by
    `Catalogs.parse_kwd`) by name, descending into BLOC children."""
    try:
        for p in params:
            if p.get("name") == name:
                return p
            if p.get("bloc"):
                inner = find_param(p.get("children", []) or [], name)
                if inner is not None:
                    return inner
    except Exception:
        return None
    return None


# ------------------------------------------------------- type compatibility


def command_return_types(cmd_obj) -> tuple:
    """Resolve `sd_prod` to a tuple of concrete output classes.

    `sd_prod` may be (a) a class, (b) a callable that returns a class
    or tuple of classes when called with `__all__=True` (the asterstudy
    convention), or (c) None.  Returns () on any failure.
    """
    try:
        sd = cmd_obj.definition.get("sd_prod") if hasattr(cmd_obj, "definition") else None
    except Exception:
        return ()
    if sd is None:
        return ()
    if isinstance(sd, type):
        return (sd,)
    if not callable(sd):
        return ()
    try:
        sig = inspect.signature(sd)
        positional = [
            p
            for p in sig.parameters.values()
            if p.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD
            and p.default is inspect.Parameter.empty
        ]
        result = sd(*([None] * len(positional)), __all__=True)
    except Exception:
        return ()
    if isinstance(result, type):
        return (result,)
    if isinstance(result, (tuple, list)):
        return tuple(t for t in result if isinstance(t, type))
    return ()


def expected_classes(param: dict) -> tuple:
    """Pull the raw class(es) the SIMP keyword expects (stored as
    `type_obj` by `parse_kwd`). Returns () when the type is a string tag
    (like "R"/"I"/"TXM"), a validator instance, or None."""
    try:
        typ = param.get("type_obj")
    except Exception:
        return ()
    if typ is None:
        return ()
    if isinstance(typ, type):
        return (typ,)
    if isinstance(typ, (tuple, list)):
        return tuple(t for t in typ if isinstance(t, type))
    return ()


def types_compatible(var_types, expected) -> bool:
    if not var_types or not expected:
        return False
    for vt in var_types:
        for et in expected:
            try:
                if issubclass(vt, et):
                    return True
            except TypeError:
                continue
    return False


# ------------------------------------------------------- value matching


_IDENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_INT_RE = re.compile(r"^-?\d+$")
_FLOAT_RE = re.compile(r"^-?(\d+\.\d*|\d*\.\d+)([eE][+-]?\d+)?$|^-?\d+[eE][+-]?\d+$")


def value_in_into(raw: str, into) -> bool:
    """True if the source-side string `raw` matches an entry in `into`."""
    raw = (raw or "").strip()
    if not raw or not into:
        return False
    try:
        for v in into:
            if isinstance(v, str):
                if raw == v:
                    return True
                if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in ("'", '"'):
                    if raw[1:-1] == v:
                        return True
            else:
                # numeric comparison
                if raw == str(v):
                    return True
                try:
                    if float(raw) == float(v):
                        return True
                except (TypeError, ValueError):
                    continue
    except Exception:
        return False
    return False


def is_bare_identifier(raw: str) -> bool:
    """True when `raw` looks like a Python variable reference (not a
    string, not a number, not a literal True/False/None)."""
    raw = (raw or "").strip().rstrip(",").strip()
    if not raw or raw in ("None", "True", "False"):
        return False
    if raw[0] in ('"', "'"):
        return False
    if _INT_RE.match(raw) or _FLOAT_RE.match(raw):
        return False
    return bool(_IDENT_RE.match(raw))


# ------------------------------------------------------- safety wrapper


def safe(fn, default=None, log_label: str | None = None):
    """Call `fn()` and swallow any exception. Returns `default` on
    failure. Used at every CATA boundary in the diagnostics path."""
    try:
        return fn()
    except Exception as exc:
        if log_label:
            sys.stderr.write(f"[diagnostics] {log_label} swallowed {type(exc).__name__}: {exc}\n")
            sys.stderr.flush()
        return default
