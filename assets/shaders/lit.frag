#version 330 core
in vec3 v_world_pos;
in vec3 v_normal;
in vec2 v_uv;

uniform sampler2D u_texture;
uniform vec3      u_tint;
uniform vec3      u_camera_pos;

uniform vec3  u_dir_light_dir;
uniform vec3  u_dir_light_color;
uniform float u_dir_light_intensity;

uniform int   u_point_count;
uniform vec3  u_point_pos[4];
uniform vec3  u_point_color[4];
uniform float u_point_intensity[4];
uniform vec3  u_point_atten[4];

out vec4 frag_color;

void main() {
    vec3 base = texture(u_texture, v_uv).rgb * u_tint;
    vec3 n = normalize(v_normal);
    vec3 v = normalize(u_camera_pos - v_world_pos);

    // Ambiente
    vec3 color = base * 0.15;

    // Luz direccional (Blinn-Phong)
    {
        vec3 l = normalize(-u_dir_light_dir);
        float diff = max(dot(n, l), 0.0);
        vec3 h = normalize(l + v);
        float spec = pow(max(dot(n, h), 0.0), 32.0);
        color += u_dir_light_color * u_dir_light_intensity * (base * diff + vec3(spec) * 0.3);
    }

    // Luces puntuales
    for (int i = 0; i < 4; i++) {
        if (i >= u_point_count) break;
        vec3 d = u_point_pos[i] - v_world_pos;
        float dist = length(d);
        vec3 l = d / dist;
        float diff = max(dot(n, l), 0.0);
        vec3 h = normalize(l + v);
        float spec = pow(max(dot(n, h), 0.0), 32.0);
        float att = 1.0 / (
            u_point_atten[i].x +
            u_point_atten[i].y * dist +
            u_point_atten[i].z * dist * dist
        );
        color += u_point_color[i] * u_point_intensity[i] * att *
                 (base * diff + vec3(spec) * 0.3);
    }

    frag_color = vec4(color, 1.0);
}
