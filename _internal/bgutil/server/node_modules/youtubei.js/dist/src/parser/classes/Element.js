import { Parser } from '../index.js';
import ChildElement from './misc/ChildElement.js';
import { YTNode, observe } from '../helpers.js';
export default class Element extends YTNode {
    static type = 'Element';
    model;
    child_elements;
    constructor(data) {
        super();
        if (Reflect.has(data, 'elementRenderer')) {
            return Parser.parseItem(data, Element);
        }
        const type = data.newElement.type.componentType;
        this.model = Parser.parseItem(type?.model);
        if (Reflect.has(data, 'newElement') && Reflect.has(data.newElement, 'childElements')) {
            this.child_elements = observe(data.newElement.childElements?.map((el) => new ChildElement(el)) || []);
        }
    }
}
//# sourceMappingURL=Element.js.map