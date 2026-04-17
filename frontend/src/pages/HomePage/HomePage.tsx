import { useState, useEffect } from 'react'
import api from '../../api/axios'
import type { HomeData } from '../../types'
import styles from './HomePage.module.scss'
import Button from '../../components/Button/Button'
import recruiterImg from '../../img/recruiter.png';
import studyOnlineImg from '../../img/study-online.jpg';
import CourseCard from '../../components/CourseCard/CourseCard'
import TeacherSlider from '../../components/TeacherSlider/TeacherSlider'


const HomePage = () => {
    const [data, setData] = useState<HomeData | null>(null)
    const [search, setSearch] = useState('')
    const [error, setError] = useState('')
    const [isLoading, setIsLoading] = useState(true)
    const PAGE_SIZE = 3
    const [visibleCount, setVisibleCount] = useState(PAGE_SIZE)


    const fetchData = async (q='') => {
        setIsLoading(true)
        setError('')
        try{
            const res = await api.get<HomeData>('/home/', {params: q ? { q } : {}})
            setData(res.data)
        } catch {
            setError('Не удалось загрузить данные')
        } finally {
            setIsLoading(false)
        }
    }

    useEffect(() => {
        fetchData()
    }, [])
    useEffect(() => {
        const timer = setTimeout(() => {
            fetchData(search)
        }, 400) 

        return () => clearTimeout(timer)
    }, [search])

    const handleSearch = (e: React.SyntheticEvent<HTMLFormElement>) => {
        e.preventDefault()
        setVisibleCount(PAGE_SIZE) 
        fetchData(search)
    }

    const visibleCourses = data?.courses.slice(0, visibleCount) ?? []
    const hasMore = (data?.courses.length ?? 0) > visibleCount

    const handleShowMore = () => {
        setVisibleCount(prev => prev + PAGE_SIZE)
    }


    return(
        <>
            <section className={`${styles.section_accent} ${styles.section}`}>
                <div className={`${styles.container} ${styles.wrapper}`}>
                    <div className={styles.contentWrapper}>
                        <div className={styles.listWrapper}>
                            <div className={styles.info}>
                                <img src="https://englex.ru/app/uploads/2026/02/icon_sale_24x24.svg" alt="" />
                                <p>Скидка до 50%</p>
                            </div>
                            <div className={`${styles.info} ${styles.info_accent}`}>
                                <img src="https://englex.ru/app/uploads/2026/03/yandex_icon_main_24x24.svg" alt="methodist-anna" />
                                <p>5.0 Рейтинг в Яндексе</p>
                            </div>
                        </div>
                        <h1 className={styles.titleFirst}>Английский, в котором вы уверены</h1>
                        <p className={styles.text}>Онлайн-школа с системным подходом и сильными преподвателями</p>
                        <Button className={styles.btn} type='button' >
                            Первый урок бесплатно
                        </Button>
                    </div>
                    <div>
                        <img className={styles.img} src={recruiterImg} alt="" />
                    </div>
                    
                </div>
                <p className={styles.recruiter}>Анна Орлан, управляет подбором и обучением преподавателей</p>

            </section>

            <section className={styles.section}>
                <div className={styles.container}>
                    <h2 className={styles.section__title}>Только 1 из 138 учителей проходит отбор в «ENGLOBE»</h2>
                    <p className={styles.section__text}>Обучаясь онлайн, трудно оценить уровень преподавателя. Мы создали авторскую систему отбора, чтобы ученики нашей онлайн-школы говорили по-английски без ошибок.</p>
                    <div className={styles.cards}>
                        <div className={styles.card}>
                            <img 
                                className={styles.card__img} 
                                src="https://englex.ru/app/uploads/icon-study-b-n.svg" alt="icon-study-b-n.svg" 
                            />
                            <h3 className={styles.card__title}>Сильные преподаватели</h3>
                            <p className={styles.card__text}>Научат говорить на английском правильно и уверенно</p>
                        </div>
                        <div className={styles.card}>
                            <img 
                                className={styles.card__img} 
                                src="https://englex.ru/app/uploads/icon-property-b-n.svg" alt="icon-study-b-n.svg" 
                            />
                            <h3 className={styles.card__title}>Обучение через общение</h3>
                            <p className={styles.card__text}>Говорите по-английски с первого урока, даже если учите язык с нуля</p>
                        </div>
                        <div className={styles.card}>
                            <img 
                                className={styles.card__img} 
                                src="https://englex.ru/app/uploads/icon-heart-app-b-n.svg" alt="icon-study-b-n.svg" 
                            />
                            <h3 className={styles.card__title}>Человеческий подход</h3>
                            <p className={styles.card__text}>Курс на индивидуальное, а не конвейерное обучение английскому</p>
                        </div>
                        
                    </div>
                </div>
            </section>

            <section className={styles.section}>
                <div className={styles.container}>
                    <h2 className={styles.section__title}>Превратите изучение английского в четкую стратегию с надежным результатом</h2>
                    <p className={styles.section__text}>Выучить язык для работы, общения, путешествий, саморазвития — какой бы ни была ваша цель, поможем ее достичь.</p>
                    
                    <form onSubmit={handleSearch} className={styles.search}>
                        <input
                            type="text"
                            value={search}
                            onChange={e => setSearch(e.target.value)}
                            placeholder="Найти курс..."
                            className={styles.search__input}
                        />
                        <Button type="submit" className={styles.search__btn}>Найти</Button>
                    </form>

                    {isLoading && <p className={styles.loading}>Загрузка...</p>}
                    {error && <p className={styles.error}>{error}</p>}

                    {!isLoading && data && (
                    <>
                        {data.courses.length === 0 ? (
                            <p className={styles.empty}>Курсы не найдены</p>
                        ) : (
                            <>
                            <div className={styles.cards}>
                                {visibleCourses.map(course => (
                                    <CourseCard key={course.id} course={course} />
                                ))}
                            </div>

                            {hasMore && (
                                <div className={styles.showMoreWrapper}>
                                    <Button
                                        type='button'
                                        onClick={handleShowMore}
                                        className={styles.btnShowMore}
                                    >
                                        Показать ещё  ({data.courses.length - visibleCount} курсов)
                                    </Button>
                                </div>
                            )}
                        </>
                        )}
                    </>
                )}

                </div>
            </section>

            <section className={styles.section}>
                <div className={styles.container}>
                    <h2 className={styles.section__title}>Обучение в удобном онлайн‑классе</h2>
                    <p className={styles.section__text}>Уроки проходят на надежной платформе, специально разработанной нашей школой для эффективного изучения английского языка. Общайтесь с преподавателем и выполняйте задания в одном окне браузера.</p>
                    
                    <div className={styles.classroom}>
                        <div className={styles.classroom__image_box}>
                            <img src={studyOnlineImg} alt="" />
                        </div>
                        <div className={styles.classroom__features}>
                            <div className={styles.feature}>
                                <div className={styles.feature__icon_wrapper}>
                                    <img src="https://englex.ru/app/uploads/icon-property-ng-d.svg" alt="" />
                                </div>
                                <div className={styles.feature__info}>
                                    <h3 className={styles.feature__title}>Все в одном месте</h3>
                                    <p className={styles.feature__text}>Быстрый доступ ко всем материалам: электронному учебнику, домашним заданиям и личному словарю</p>
                                </div>
                            </div>
                            <div className={styles.feature}>
                                <div className={styles.feature__icon_wrapper}>
                                    <img src="https://englex.ru/app/uploads/icon-social-ng-d.svg" alt="" />
                                </div>
                                <div >
                                    <h3 className={styles.feature__title}>Совместная работа</h3>
                                    <p className={styles.feature__text}>Во время урока преподаватель сразу видит ваши ответы, исправляет и подробно объясняет ошибки</p>
                                </div>
                            </div>
                            <div className={styles.feature}>
                                <div className={styles.feature__icon_wrapper}>
                                    <img src="https://englex.ru/app/uploads/icon-settings-ng-d.svg" alt="" />
                                </div>
                                <div >
                                    <h3 className={styles.feature__title}>Адаптивный учебник</h3>
                                    <p className={styles.feature__text}>Преподаватель добавляет в электронный учебник упражнения, которые полезны и интересны именно вам</p>
                                </div>
                            </div>
                        </div>
                </div>
                </div>
            </section>

            <section className={styles.section}>
                <div className={styles.container}>
                    <h2 className={styles.section__title}>Преподаватели — мастера своего дела</h2>
                    <p className={styles.section__text}>Прогресс, мотивация и сроки обучения на 50% зависят от преподавателя. Не теряйте время, доверьте свой английский экспертам, которые прошли наш строгий отбор.</p>
                    
                    {isLoading && <p className={styles.loading}>Загрузка...</p>}
                    {error && <p className={styles.error}>{error}</p>}

                    {!isLoading && data && (
                        <>
                            {data.teachers.length === 0 
                                ? (<p className={styles.empty}>Преподаватели не найдены</p>) 
                                : (<TeacherSlider teachers={data.teachers} />)}
                        </>
                    )}
                </div>
            </section>


            {!isLoading && data && (
                <section className={`${styles.section} ${styles.section_accent}`}>
                    <div className={styles.container}>
                        <h2 className={styles.section__title}>Школа в цифрах</h2>
                        <div className={styles.stats}>
                            <div className={styles.stat}>
                                <span className={styles.stat__number}>{data.stats.total_courses}</span>
                                <span className={styles.stat__label}>Курсов</span>
                            </div>
                            <div className={styles.stat}>
                                <span className={styles.stat__number}>{data.stats.total_lessons}</span>
                                <span className={styles.stat__label}>Уроков</span>
                            </div>
                            <div className={styles.stat}>
                                <span className={styles.stat__number}>{data.stats.total_students}</span>
                                <span className={styles.stat__label}>Студентов</span>
                            </div>
                            <div className={styles.stat}>
                                <span className={styles.stat__number}>{data.stats.avg_score ?? '—'}</span>
                                <span className={styles.stat__label}>Средний балл</span>
                            </div>
                            {data.stats.top_level && (
                                <div className={styles.stat}>
                                    <span className={styles.stat__number}>{data.stats.top_level}</span>
                                    <span className={styles.stat__label}>Популярный уровень</span>
                                </div>
                            )}
                        </div>
                    </div>
                </section>
            )}

        </>
    )

}

export default HomePage