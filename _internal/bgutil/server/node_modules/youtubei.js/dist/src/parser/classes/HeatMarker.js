import { YTNode } from '../helpers.js';
export default class HeatMarker extends YTNode {
    static type = 'HeatMarker';
    time_range_start_millis;
    marker_duration_millis;
    heat_marker_intensity_score_normalized;
    constructor(data) {
        super();
        this.time_range_start_millis = Number.parseInt(data.startMillis, 10);
        this.marker_duration_millis = Number.parseInt(data.durationMillis, 10);
        this.heat_marker_intensity_score_normalized = data.intensityScoreNormalized;
    }
}
//# sourceMappingURL=HeatMarker.js.map