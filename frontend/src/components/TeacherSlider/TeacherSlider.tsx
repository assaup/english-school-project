import { useState } from "react";
import type { Teacher } from "../../types";
import TeacherCard from "../TeacherCard/TeacherCard";
import styles from "./TeacherSlider.module.scss";

interface props {
    teachers: Teacher[];
}

const TeacherSlider = ({ teachers }: props) => {
    const getVisible = () => {
        if (window.innerWidth <= 768) return 1;
        if (window.innerWidth <= 1024) return 2;
        return 3;
    };
    const [current, setCurrent] = useState(0);
    const [visible, setVisible] = useState(getVisible());
    const max = Math.max(0, teachers.length - visible)
    useState(() => {
        const handleResize = () => {
            setVisible(getVisible())
            setCurrent(0)
        }

        window.addEventListener("resize", handleResize)
        return () => window.removeEventListener("resize", handleResize)
    })
    const prev = () => setCurrent((c) => Math.max(0, c - 1));
    const next = () => setCurrent((c) => Math.max(0, c + 1));

    return (
        <div className={styles.slider} role="region" aria-label="Карусель преподавателей">
            <button
                className={`${styles.arrow} ${styles.arrowLeft}`}
                onClick={prev}
                disabled={current === 0}
                aria-label="Предыдущий слайд"
            >
                ←
            </button>
            <div className={styles.card_container}>
                <div
                    className={styles.inner}
                    style={{
                        transform: `translateX(-${current * (100 / visible)}%)`
                    }}
                >
                    {teachers.map((teacher) => (
                        <div key={teacher.id} className={styles.slide}>
                            <TeacherCard teacher={teacher} />
                        </div>
                    ))}
                </div>
            </div>
            <button
                className={`${styles.arrow} ${styles.arrowRight}`}
                onClick={next}
                disabled={current === max}
                aria-label="Следующий слайд"
            >
                →
            </button>
            <div className={styles.dots}>
                {Array.from({ length: max + 1 }, (_, i) => (
                    <button
                        key={i}
                        className={`${styles.dot} ${i === current ? styles.dotActive : ""}`}
                        onClick={() => setCurrent(i)}
                        aria-label={`Перейти к слайду ${i + 1}`}
                        aria-current={i === current ? "true" : "false"}
                    />
                ))}
            </div>
        </div>
    );
};

export default TeacherSlider;
