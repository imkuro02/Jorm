shader_type canvas_item;

uniform sampler2D screen_texture : hint_screen_texture, filter_linear;

uniform bool grayscale_enabled = true;

void fragment() {
    vec4 c = texture(screen_texture, SCREEN_UV);

    if (grayscale_enabled) {
        float gray = dot(c.rgb, vec3(0.299, 0.587, 0.114));
        c.rgb = vec3(gray);
    }

    COLOR = c;
}