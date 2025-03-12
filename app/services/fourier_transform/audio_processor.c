#include <fftw3.h>
#include <math.h>

void calculate_spectrum(double *audio_buffer, int buffer_size, double *output)
{
    fftw_complex *out;
    fftw_plan plan;

    out = (fftw_complex *)fftw_malloc(sizeof(fftw_complex) * (buffer_size / 2 + 1));
    plan = fftw_plan_dft_r2c_1d(buffer_size, audio_buffer, out, FFTW_ESTIMATE);

    fftw_execute(plan);

    // Correct access to complex numbers through FFTW structure
    for (int i = 0; i < buffer_size / 2 + 1; i++)
    {
        output[i] = sqrt(out[i][0] * out[i][0] + out[i][1] * out[i][1]);
    }

    fftw_destroy_plan(plan);
    fftw_free(out);
}