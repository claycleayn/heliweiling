#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <time.h>

int main(int argc, char *argv[]) {
    // 使用当前时间 + 进程 ID 作为随机种子，保证每个容器不同
    srand(time(NULL) ^ getpid());

    // 参数：采样次数（可从命令行参数获取，默认为100）
    int samples = 20;
    if (argc > 1) samples = atoi(argv[1]);

    const char *outfile = "sensor_data.csv";
    FILE *fp = fopen(outfile, "w");
    if (fp == NULL) {
        perror("无法创建文件");
        return 1;
    }
    fprintf(fp, "sample_id,temperature\n");

    double temp = 20.0;  // 初始温度
    for (int i = 1; i <= samples; i++) {
        // 随机游走：变化范围 [-0.5, 0.5]
        double delta = ((double)rand() / RAND_MAX) - 0.5;  // [-0.5,0.5]
        temp += delta;
        // 限制合理范围（可选）

        fprintf(fp, "%d,%.2f\n", i, temp);
        fflush(fp);   // 确保实时写入

        printf("[采样 #%d] 温度 = %.2f °C\n", i, temp);
        usleep(500000);  // 0.5 秒
    }

    fclose(fp);
    printf("采样完成，数据已写入 %s\n", outfile);
    return 0;
}