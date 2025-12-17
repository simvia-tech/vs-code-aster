# -*- coding: utf-8 -*-

# Copyright 2016 EDF R&D i
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License Version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, you may download a copy of license
# from https://www.gnu.org/licenses/gpl-3.0.

"""
Const-correctness
-----------------

Implementation of Stage const-correctness.

This protects executed stages from incidental modifications.

If a modification is asked on an executed stage, it is automatically
copied. The modification is performed on the original, leaving the copy
unchanged. The copy is declared as executed: thus, the executed stage
can still be consulted in its original state.

This happens when requiring a modification on a stage
that is referenced by the current case as well as a runcase.
"""


from functools import wraps

class CopyUnderProgress:
    """
    Context manager under which the auto copy operation
        should be done. This toggles a "copy under progress"
        flag.

    Arguments:
        reset_to (bool): tells to what value to reset
           the "copy under progress" flag once context
           manager is exited.
    """
    def __init__(self, reset_to=False):
        """Initializer"""
        self.reset_to = reset_to

    def __enter__(self):
        """Actions when entering the context"""
        ModifiesStageInstance.COPY_UNDER_PROGRESS = True

    def __exit__(self, *args):
        """Actions when leaving the context"""
        ModifiesStageInstance.COPY_UNDER_PROGRESS = self.reset_to

class ModifiesStageInstance:
    """
    This decorator indicates a *Stage* method that should modify its instance.

    Therefore, the stage is auto copied before the decorated method is invoked.

    Attributes:
        COPY_UNDER_PROGRESS (bool): Class attribute declaring set to *True*
            when a auto-copy operation is already under progress.
            In this case, the autocopy operation should not be called again.
    """

    COPY_UNDER_PROGRESS = False

    def __init__(self, enabled):
        """
        Initialize decorator.

        When set to *False*, decorator argument `enabled` prevents
            any automatic copy. This is useful to tag auto-copy
            methods themselves, to protect them against infinite auto copy
            invocation when calling their sub-methods.
        """

        self.enabled = enabled

    def __call__(self, method):
        """
        Implementation of the decorator
        """

        @wraps(method)
        def wrapper(this, *args, **kwargs):
            """Wrapper"""

            # If an auto copy is already under progress
            #     just invoke the method.
            if type(self).COPY_UNDER_PROGRESS:
                return method(this, *args, **kwargs)

            # Ibid for autocopy methods themselves.
            # Disable auto-copy when they are invoked,
            #     to avoid infinite recursion.
            if not self.enabled:
                with CopyUnderProgress(reset_to=type(self).COPY_UNDER_PROGRESS):
                    return method(this, *args, **kwargs)

            # Ibid if auto copy is not enabled in the root data model
            # (only for some unittests)
            if not this.model.autocopy_enabled:
                return method(this, *args, **kwargs)

            # Copy the stage
            # Perform modification on the original
            with CopyUnderProgress(reset_to=False):
                this.autocopy()
                return method(this, *args, **kwargs)

        return wrapper

class ModifiesCommandInstance:
    """
    This decorator indicates a *Command* method that should modify its instance.

    If the *Stage* containing it is an executed one, it has to be copied,
        so that the modification applies to the original only, with
        a copy that can still be consulted in its original state.
    """

    def __init__(self, enabled):
        """
        Initializer. The `enabled` argument has the same meaning as
        in *ModifiesStageInstance* class.
        """
        self.enabled = enabled

    def __call__(self, method):
        """Implementation of the decorator"""

        @wraps(method)
        def wrapper(this, *args, **kwargs):
            """Wrapper"""

            from .basic import Command

            # If a auto copy is already under progress
            #     proceed normally.
            if ModifiesStageInstance.COPY_UNDER_PROGRESS:
                return method(this, *args, **kwargs)

            if not self.enabled:
                with CopyUnderProgress(\
                        reset_to=ModifiesStageInstance.COPY_UNDER_PROGRESS):
                    return method(this, *args, **kwargs)

            # Otherwise, copy containing stage before
            #     performing modification.
            with CopyUnderProgress(reset_to=False):

                # If the instance is a *Command*
                if isinstance(this, Command):

                    # If auto copy is enabled in the root data model
                    # (always true except for some unittests)
                    if this.model.autocopy_enabled:
                        this.autocopy()

                    return method(this, *args, **kwargs)

                # Otherwise, the instance is a type that is aggregated
                #     by a *Command*.
                #     Then start by finding the containing command.
                cmd = this
                while not isinstance(cmd, Command):
                    cmd = cmd._engine # pragma pylint: disable=protected-access

                # Apply the same procedure then
                if cmd.model.autocopy_enabled:
                    cmd.autocopy()

                return method(this, *args, **kwargs)

        return wrapper
