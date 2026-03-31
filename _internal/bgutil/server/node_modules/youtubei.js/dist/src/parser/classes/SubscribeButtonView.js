import { YTNode } from '../helpers.js';
import NavigationEndpoint from './NavigationEndpoint.js';
export default class SubscribeButtonView extends YTNode {
    static type = 'SubscribeButtonView';
    subscribe_button_content;
    unsubscribe_button_content;
    disable_notification_bell;
    button_style;
    is_signed_out;
    background_style;
    disable_subscribe_button;
    on_show_subscription_options;
    channel_id;
    enable_subscribe_button_post_click_animation;
    bell_accessiblity_data;
    constructor(data) {
        super();
        this.subscribe_button_content = this.#parseButtonContent(data.subscribeButtonContent);
        this.unsubscribe_button_content = this.#parseButtonContent(data.unsubscribeButtonContent);
        this.disable_notification_bell = data.disableNotificationBell;
        this.button_style = {
            unsubscribed_state_style: data.buttonStyle.unsubscribedStateStyle,
            subscribed_state_style: data.buttonStyle.subscribedStateStyle
        };
        this.is_signed_out = data.isSignedOut;
        this.background_style = data.backgroundStyle;
        this.disable_subscribe_button = data.disableSubscribeButton;
        this.on_show_subscription_options = new NavigationEndpoint(data.onShowSubscriptionOptions);
        this.channel_id = data.channelId;
        this.enable_subscribe_button_post_click_animation = data.enableSubscribeButtonPostClickAnimation;
        this.bell_accessiblity_data = {
            off_label: data.bellAccessibilityData.offLabel,
            all_label: data.bellAccessibilityData.allLabel,
            occasional_label: data.bellAccessibilityData.occasionalLabel,
            disabled_label: data.bellAccessibilityData.disabledLabel
        };
    }
    #parseButtonContent(data) {
        return {
            button_text: data.buttonText,
            accessibility_text: data.accessibilityText,
            image_name: data.imageName,
            subscribe_state_subscribed: data.subscribeState.subscribed,
            endpoint: new NavigationEndpoint(data.onTapCommand)
        };
    }
}
//# sourceMappingURL=SubscribeButtonView.js.map