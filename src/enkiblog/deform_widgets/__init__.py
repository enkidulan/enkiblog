import json
from deform.widget import TextInputWidget, null


class CKEditorWidget(TextInputWidget):

    readonly_template = 'readonly/ckeditor'
    delayed_load = False
    strip = True
    template = 'ckeditor'
    requirements = (('ckeditor', None), )

    default_options = {
        'height': 500,
    }
    options = None

    def serialize(self, field, cstruct, **kw):
        if cstruct in (null, None):
            cstruct = ''

        readonly = kw.get('readonly', self.readonly)
        template = self.readonly_template if readonly else self.template

        options = dict(self.default_options)
        options_overrides = dict(kw.get('options', self.options or {}))
        options.update(options_overrides)
        kw['ckeditor_options'] = json.dumps(options)[1:-1]

        values = self.get_template_values(field, cstruct, kw)
        return field.renderer(template, **values)
