# Original license
# Copyright (c) 2022 Torchbox Ltd and individual contributors.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#     1. Redistributions of source code must retain the above copyright notice,
#        this list of conditions and the following disclaimer.
#
#     2. Redistributions in binary form must reproduce the above copyright
#        notice, this list of conditions and the following disclaimer in the
#        documentation and/or other materials provided with the distribution.
#
#     3. Neither the name of Torchbox nor the names of its contributors may be used
#        to endorse or promote products derived from this software without
#        specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# Django
from django import forms


class Options:
    """
    An object that serves as a container for configuration options. When a class is defined using
    OptionCollectingMetaclass as its metaclass, any attributes defined on an inner `class Meta`
    will be copied to an Options instance which will then be accessible as the class attribute
    `_meta`.

    The base Options class has no functionality of its own, but exists so that specific
    configuration options can be defined as mixins and collectively merged in to either Options or
    another base class with the same interface such as django.forms.models.ModelFormOptions,
    to arrive at a final class that recognises the desired set of options.
    """

    def __init__(self, options=None):
        pass


class OptionCollectingMetaclass(type):
    """
    Metaclass that handles inner `class Meta` definitions. When a class using
    OptionCollectingMetaclass defines an inner Meta class and an `options_class` attribute
    specifying an Options class, an Options object will be created from it and set as the class
    attribute `_meta`.
    """

    options_class = None

    def __new__(mcs, name, bases, attrs):
        new_class = super().__new__(mcs, name, bases, attrs)
        if mcs.options_class:
            new_class._meta = mcs.options_class(getattr(new_class, "Meta", None))
        return new_class


class PermissionedFormOptionsMixin:
    """Handles the field_permissions option for PermissionedForm"""

    def __init__(self, options=None):
        super().__init__(options)
        self.field_permissions = getattr(options, "field_permissions", None)


class PermissionedFormOptions(PermissionedFormOptionsMixin, Options):
    """Options class for PermissionedForm"""


FormMetaclass = type(forms.Form)


class PermissionedFormMetaclass(OptionCollectingMetaclass, FormMetaclass):
    """
    Extends the django.forms.Form metaclass with support for an inner `class Meta` that accepts
    a `field_permissions` configuration option
    """

    options_class = PermissionedFormOptions


class PermissionedForm(forms.Form, metaclass=PermissionedFormMetaclass):
    """
    An extension to `django.forms.Form` to accept an optional `for_user` keyword argument
    indicating the user the form will be presented to.

    Any fields named in the `field_permissions` dict in Meta will apply a permission test on the
    named permission using `User.has_perm`; if the user lacks that permission, the field will be
    omitted from the form.
    """

    def __init__(self, *args, for_user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if for_user:
            field_perms = self._meta.field_permissions or {}
            for field_name, perm in field_perms.items():
                if not for_user.has_perm(perm):
                    del self.fields[field_name]


class PermissionedModelFormOptions(
    PermissionedFormOptionsMixin, forms.models.ModelFormOptions
):
    """
    Options class for PermissionedModelForm; extends ModelForm's options to accept
    `field_permissions`
    """


class PermissionedModelFormMetaclass(
    PermissionedFormMetaclass, forms.models.ModelFormMetaclass
):
    """
    Metaclass for PermissionedModelForm; extends the ModelForm metaclass to use
    PermissionedModelFormOptions in place of ModelFormOptions and thus accept the
    `field_permissions` option.

    Note that because ModelForm does not participate in the OptionCollectingMetaclass logic, this
    has the slightly hacky effect of letting ModelFormMetaclass construct a ModelFormOptions object
    for the lifetime of ModelFormMetaclass.__new__, which we promptly throw out and recreate as a
    PermissionedModelFormOptions object.
    """

    options_class = PermissionedModelFormOptions


class PermissionedModelForm(
    PermissionedForm, forms.ModelForm, metaclass=PermissionedModelFormMetaclass
):
    """A ModelForm that implements the `for_user` keyword argument from PermissionedForm"""
