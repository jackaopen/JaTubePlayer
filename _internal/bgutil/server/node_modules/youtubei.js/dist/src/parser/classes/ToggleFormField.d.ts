import { type RawNode } from '../index.js';
import { YTNode } from '../helpers.js';
import NavigationEndpoint from './NavigationEndpoint.js';
export default class ToggleFormField extends YTNode {
    static type: string;
    label: Text;
    toggled: boolean;
    toggle_on_action?: NavigationEndpoint;
    toggle_off_action?: NavigationEndpoint;
    constructor(data: RawNode);
}
