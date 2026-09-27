import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import time


class MoverNode(Node):

    def __init__(self):
        super().__init__('mover_node')

        # =====================================================
        # 1. PUBLISHER
        # =====================================================

        self.publisher_ = self.create_publisher(
            Twist,
            'cmd_vel',
            10
        )

        # Program dijalankan setiap 0.1 detik
        self.timer = self.create_timer(
            0.1,
            self.timer_callback
        )

        # =====================================================
        # 2. PARAMETER ROBOT
        # =====================================================

        self.linear_speed = 1.0       # m/s
        self.angular_speed = 0.5      # rad/s

        # Ukuran persegi panjang
        self.length = 5.0             # meter
        self.width = 4.0              # meter

        # =====================================================
        # 3. PERHITUNGAN WAKTU
        # =====================================================

        # Waktu untuk sisi panjang
        self.length_time = (
            self.length / self.linear_speed
        )

        # Waktu untuk sisi lebar
        self.width_time = (
            self.width / self.linear_speed
        )

        # Waktu untuk berputar 90 derajat
        self.turn_time = (
            (3.14159265359 / 2.0)
            / self.angular_speed
        )

        # =====================================================
        # 4. KONDISI AWAL ROBOT
        # =====================================================

        # Nomor sisi: 0, 1, 2, 3
        self.side = 0

        # Kondisi awal = bergerak maju
        self.state = 'forward'

        # Waktu awal gerakan
        self.start_time = time.time()

        self.get_logger().info(
            'Robot mulai membentuk persegi panjang...'
        )


    # =========================================================
    # 5. KONTROL GERAK ROBOT
    # =========================================================

    def timer_callback(self):

        msg = Twist()

        current_time = time.time()

        # Lama robot berada pada kondisi saat ini
        elapsed_time = (
            current_time - self.start_time
        )


        # =====================================================
        # A. GERAK MAJU
        # =====================================================

        if self.state == 'forward':

            # Robot bergerak maju
            msg.linear.x = float(self.linear_speed)

            # Tidak berputar
            msg.angular.z = 0.0

            # -------------------------------------------------
            # Menentukan panjang sisi
            # -------------------------------------------------

            if self.side == 0 or self.side == 2:

                # Sisi 1 dan 3 = panjang
                target_time = self.length_time

            else:

                # Sisi 2 dan 4 = lebar
                target_time = self.width_time

            # -------------------------------------------------
            # Jika sisi sudah selesai
            # -------------------------------------------------

            if elapsed_time >= target_time:

                # Beralih ke kondisi berputar
                self.state = 'turn'

                # Reset waktu
                self.start_time = current_time

                self.get_logger().info(
                    f'Sisi {self.side + 1} selesai → '
                    'Putar 90 derajat'
                )


        # =====================================================
        # B. PUTAR 90 DERAJAT
        # =====================================================

        elif self.state == 'turn':

            # Tidak bergerak maju
            msg.linear.x = 0.0

            # Berputar
            msg.angular.z = float(self.angular_speed)

            # -------------------------------------------------
            # Jika putaran sudah selesai
            # -------------------------------------------------

            if elapsed_time >= self.turn_time:

                # Pindah ke sisi berikutnya
                self.side += 1

                # Reset waktu
                self.start_time = current_time

                # -------------------------------------------------
                # Jika sudah melewati 4 sisi
                # -------------------------------------------------

                if self.side >= 4:

                    self.state = 'stop'

                    self.get_logger().info(
                        'Keempat sisi selesai → Robot berhenti'
                    )

                else:

                    self.state = 'forward'

                    self.get_logger().info(
                        f'Mulai sisi {self.side + 1}'
                    )


        # =====================================================
        # C. BERHENTI
        # =====================================================

        elif self.state == 'stop':

            # Semua kecepatan = 0
            msg.linear.x = 0.0
            msg.angular.z = 0.0

            self.publisher_.publish(msg)

            self.get_logger().info(
                'Robot berhenti.'
            )

            # Hentikan timer
            self.timer.cancel()

            return


        # =====================================================
        # KIRIM PERINTAH KE ROBOT
        # =====================================================

        self.publisher_.publish(msg)


# =============================================================
# 6. MENJALANKAN PROGRAM
# =============================================================

def main(args=None):

    rclpy.init(args=args)

    node = MoverNode()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
