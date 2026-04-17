import { useState } from "react";
import type { Teacher } from "../../types";
import TeacherCard from "../TeacherCard/TeacherCard";
import styles from './TeacherSlider.module.scss'

interface props {
    teachers: Teacher[]
}

const TeacherSlider = ({teachers}: props) => {
    const [current, setCurrent] = useState(0)
    const visible = 3
    const max = Math.max(0, teachers.length - visible)

    const prev = () => setCurrent(c => Math.max(0, c - 1))
    const next = () => setCurrent(c => Math.max(0, c + 1))

    return (
        <div className={styles.slider}>
            <button
                className={`${styles.arrow} ${styles.arrowLeft}`}
                onClick={prev}
                disabled={current === 0}
            >
                ←
            </button>
            <div className={styles.card_container}>
                <div
                    className={styles.inner}
                    style={{ transform: `translateX(calc(-${current} * (100% / ${visible} + 20px / ${visible})))`}}
                >
                    {teachers.map(teacher => (
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
            >
                →
            </button>
            <div className={styles.dots}>
                {Array.from({ length: max + 1 }, (_, i) => (
                    <button
                        key={i}
                        className={`${styles.dot} ${i === current ? styles.dotActive : ''}`}
                        onClick={() => setCurrent(i)}
                    />
                ))}
            </div>
        </div>
        
    )
}

export default TeacherSlider