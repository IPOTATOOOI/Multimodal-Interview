package com.example.spr_swcup.service.Impl;
import com.example.spr_swcup.common.Result;
import com.example.spr_swcup.dto.positionInfo.PositionInfoDTO;
import com.example.spr_swcup.entity.*;
import com.example.spr_swcup.mapper.positionInfo.*;
import com.example.spr_swcup.service.PositionInfoService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * @author lty
 * @version 1.0
 * {@code @description:}
 * @since 2025-07-19
 */
@Service
@RequiredArgsConstructor
public class PositionInfoServiceImpl implements PositionInfoService {

    private final DomainMapper domainMapper;
    private final PositionMapper positionMapper;
    private final CoreCompetenceMapper coreCompetenceMapper;
    private final TermMapper termMapper;
    private final HighFreqQuestionMapper highFreqQuestionMapper;


    @Override
    public Result<PositionInfoDTO> getPositionInfo(String domainName, String positionName) {

        // 1. 查询领域
        Domain domain = domainMapper.findByDomainName(domainName);
        if (domain == null) {
            return Result.fail(404, "未找到该领域");
        }

        // 2. 查询岗位
        Position position = positionMapper.findByPositionNameAndDomainId(
                positionName,
                domain.getDomainId()
        );
        if (position == null) {
            return Result.fail(404, "未找到该岗位");
        }

        // 3. 查询核心能力
        List<CoreCompetence> coreCompetences = coreCompetenceMapper.findByPositionId(
                position.getPositionId()
        );

        // 4. 查询术语
        List<Term> terms = termMapper.findByPositionId(
                position.getPositionId()
        );

        // 5. 查询高频问题
        List<HighFreqQuestion> highFreqQuestions = highFreqQuestionMapper.findByPositionId(
                position.getPositionId()
        );

        // 封装结果
        PositionInfoDTO dto = new PositionInfoDTO();
        dto.setCoreCompetences(coreCompetences);
        dto.setTerms(terms);
        dto.setHighFreqQuestions(highFreqQuestions);

        return Result.success(dto);
    }
}
