import { YTNode } from '../helpers.js';
export default class ClipCreationScrubber extends YTNode {
    static type = 'ClipCreationScrubber';
    length_template;
    max_length_ms;
    min_length_ms;
    default_length_ms;
    window_size_ms;
    start_label;
    end_label;
    duration_label;
    constructor(data) {
        super();
        this.length_template = data.lengthTemplate;
        this.max_length_ms = data.maxLengthMs;
        this.min_length_ms = data.minLengthMs;
        this.default_length_ms = data.defaultLengthMs;
        this.window_size_ms = data.windowSizeMs;
        this.start_label = data.startAccessibility?.accessibilityData?.label;
        this.end_label = data.endAccessibility?.accessibilityData?.label;
        this.duration_label = data.durationAccessibility?.accessibilityData?.label;
    }
}
//# sourceMappingURL=ClipCreationScrubber.js.map