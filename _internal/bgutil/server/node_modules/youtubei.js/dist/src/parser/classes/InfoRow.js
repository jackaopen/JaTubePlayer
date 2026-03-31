import { YTNode } from '../helpers.js';
import { Text } from '../misc.js';
export default class InfoRow extends YTNode {
    static type = 'InfoRow';
    title;
    default_metadata;
    expanded_metadata;
    info_row_expand_status_key;
    constructor(data) {
        super();
        this.title = new Text(data.title);
        if (Reflect.has(data, 'defaultMetadata')) {
            this.default_metadata = new Text(data.defaultMetadata);
        }
        if (Reflect.has(data, 'expandedMetadata')) {
            this.expanded_metadata = new Text(data.expandedMetadata);
        }
        if (Reflect.has(data, 'infoRowExpandStatusKey')) {
            this.info_row_expand_status_key = data.infoRowExpandStatusKey;
        }
    }
}
//# sourceMappingURL=InfoRow.js.map