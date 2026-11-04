#version 330 core
in vec2 v_uv;

uniform sampler2D u_texture;
uniform vec4      u_uv_rect;   // (x, y, w, h)
uniform vec4      u_tint;      // RGBA
uniform float     u_flip_x;    // +1.0 normal, -1.0 flip
uniform float     u_flip_y;

out vec4 frag_color;

void main() {
    vec2 uv = v_uv;
    if (u_flip_x < 0.0) uv.x = 1.0 - uv.x;
    if (u_flip_y < 0.0) uv.y = 1.0 - uv.y;
    uv = uv * u_uv_rect.zw + u_uv_rect.xy;

    vec4 t = texture(u_texture, uv) * u_tint;
    if (t.a < 0.01) discard;
    frag_color = t;
}
