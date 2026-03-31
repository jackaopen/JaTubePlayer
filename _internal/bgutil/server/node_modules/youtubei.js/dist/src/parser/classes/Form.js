import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import ToggleFormField from './ToggleFormField.js';
export default class Form extends YTNode {
    static type = 'Form';
    fields;
    constructor(data) {
        super();
        this.fields = Parser.parseArray(data.fields, ToggleFormField);
    }
}
//# sourceMappingURL=Form.js.map