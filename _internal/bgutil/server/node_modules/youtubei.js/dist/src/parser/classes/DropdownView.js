import { YTNode } from '../helpers.js';
import { Text, Thumbnail } from '../misc.js';
import NavigationEndpoint from './NavigationEndpoint.js';
export default class DropdownView extends YTNode {
    static type = 'DropdownView';
    label;
    placeholder_text;
    disabled;
    options;
    dropdown_type;
    id;
    constructor(data) {
        super();
        this.label = new Text(data.label);
        this.placeholder_text = new Text(data.placeholderText);
        this.disabled = !!data.disabled;
        this.dropdown_type = data.type;
        this.id = data.id;
        if (Reflect.has(data, 'options')) {
            this.options = data.options.map((option) => ({
                title: new Text(option.title),
                subtitle: new Text(option.subtitle),
                leading_image: Thumbnail.fromResponse(option.leadingImage),
                value: { privacy_status_value: option.value?.privacyStatusValue },
                on_tap: new NavigationEndpoint(option.onTap),
                is_selected: !!option.isSelected
            }));
        }
    }
}
//# sourceMappingURL=DropdownView.js.map