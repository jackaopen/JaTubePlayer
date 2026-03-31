import { YTNode } from '../helpers.js';
import { type RawNode } from '../index.js';
import { type ObservedArray } from '../helpers.js';
import ToggleFormField from './ToggleFormField.js';
export default class Form extends YTNode {
    static type: string;
    fields: ObservedArray<ToggleFormField>;
    constructor(data: RawNode);
}
