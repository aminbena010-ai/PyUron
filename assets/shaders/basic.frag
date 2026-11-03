#version 330 core
in vec2 v_uv;

uniform sampler2D u_texture;
uniform vec3      u_tint;

out vec4 frag_color;

void main() {
    vec4 t = texture(u_texture, v_uv);
    frag_color = vec4(t.rgb * u_tint, t.a);
}
