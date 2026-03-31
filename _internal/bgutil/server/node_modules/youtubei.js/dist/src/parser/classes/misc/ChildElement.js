import { YTNode } from '../../helpers.js';
export default class ChildElement extends YTNode {
    static type = 'ChildElement';
    text;
    properties;
    child_elements;
    constructor(data) {
        super();
        if (Reflect.has(data, 'type') && Reflect.has(data.type, 'textType')) {
            this.text = data.type.textType.text?.content;
        }
        this.properties = data.properties;
        if (Reflect.has(data, 'childElements')) {
            this.child_elements = data.childElements.map((el) => new ChildElement(el));
        }
    }
}
//# sourceMappingURL=ChildElement.js.map