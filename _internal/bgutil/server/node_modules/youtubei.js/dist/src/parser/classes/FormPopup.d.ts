import { YTNode } from '../helpers.js';
import { type RawNode } from '../index.js';
import { type ObservedArray } from '../helpers.js';
import Text from './misc/Text.js';
import Form from './Form.js';
import Button from './Button.js';
export default class FormPopup extends YTNode {
    static type: string;
    title: Text;
    form: Form | null;
    buttons: ObservedArray<Button>;
    constructor(data: RawNode);
}
