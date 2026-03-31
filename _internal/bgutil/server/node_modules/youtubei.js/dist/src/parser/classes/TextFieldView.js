import { YTNode } from '../helpers.js';
export default class TextFieldView extends YTNode {
    static type = 'TextFieldView';
    display_properties;
    content_properties;
    initial_state;
    form_field_metadata;
    constructor(data) {
        super();
        if (Reflect.has(data, 'displayProperties')) {
            this.display_properties = {
                isMultiline: !!data.displayProperties.isMultiline,
                disableNewLines: !!data.displayProperties.disableNewLines
            };
        }
        if (Reflect.has(data, 'contentProperties')) {
            this.content_properties = {
                labelText: data.contentProperties.labelText,
                placeholderText: data.contentProperties.placeholderText,
                maxCharacterCount: data.contentProperties.maxCharacterCount
            };
        }
        if (Reflect.has(data, 'initialState')) {
            this.initial_state = {
                isFocused: !!data.initialState.isFocused
            };
        }
        if (Reflect.has(data, 'formFieldMetadata')) {
            this.form_field_metadata = {
                formId: data.formFieldMetadata.formId,
                fieldId: data.formFieldMetadata.fieldId
            };
        }
    }
}
//# sourceMappingURL=TextFieldView.js.map