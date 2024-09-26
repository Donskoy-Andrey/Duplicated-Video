import React, {useState, useEffect} from 'react';
import OverlayTrigger from 'react-bootstrap/OverlayTrigger';
import Tooltip from 'react-bootstrap/Tooltip';

export const Categories = (props) => {
    const [screenWidth, setScreenWidth] = useState(window.innerWidth);

    useEffect(() => {
        const handleResize = () => {
            setScreenWidth(window.innerWidth);
        };
        window.addEventListener('resize', handleResize);
        return () => {
            window.removeEventListener('resize', handleResize);
        };
    }, []);

    const responseData = props.responseData['files'];
    const status = props.responseData['status'];

    // console.log(responseData)

    const getCls = (key) => {
        const validType = responseData[key]['valid_type'];
        let cls = '';
        switch (validType) {
            case 'Неожиданная категория':
                cls = "bg-red";
                break;
            case 'Правильный документ':
                cls = "bg-green";
                break;
            case 'Лишний документ':
                cls = "bg-yellow";
                break;
            default:
                if (validType.startsWith("Неожиданная категория")) {
                    cls = "bg-red";
                }
                break;
        }
        return cls;
    }

    const getDisplayKey = (key) => {
        const validType = responseData[key]['valid_type'];
        if (screenWidth < 480 && key.length > 15) {
            const shortKey = `${key.substring(0, 5)}...${key.substring(key.length - 10)}`;
            return (
                    <span className={`response-file__key`}>
                        <code>{shortKey}</code>
                    </span>
            );
        }
        return (
            <span className="response-file__key">
                <code>{key}</code>
            </span>
        )
            ;
    };

    return (
        <div>
            {
                status === 'ok' ?
                    <div className="status ok">Ошибок не обнаружено</div> :
                    <div className="status bad">Ошибки обнаружены</div>
            }
            {Object.keys(responseData).map(fileKey => (
                <OverlayTrigger
                    key={`overlay-${fileKey}`}
                    placement="top"
                    overlay={<Tooltip id={`tooltip-${fileKey}`}>{responseData[fileKey]['valid_type']}</Tooltip>}
                >
                    <div className={`response-file__container ${getCls(fileKey)}`} key={`container-${fileKey}`}>
                        {getDisplayKey(fileKey)}
                        <span className="response-file__category">
                {responseData[fileKey].category}
            </span>
                    </div>
                </OverlayTrigger>
            ))}
        </div>
    );
};
